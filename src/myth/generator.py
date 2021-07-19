import time
import json
from datetime import datetime
from multiprocessing import Process

from myth.sink import KafkaSink, ConsoleSink, ClickhouseSink
from myth.influx import InfluxSink

from faker import Faker

def generate_concurrent(config_file, concurrency):
    print(config_file, concurrency)
    workers = []
    for i in range(concurrency):
        generator = DataGenerator(config_file, f'worker{i}')
        print(f'create {i} worker for write data')
        w = Process(target=generator.load)
        w.start()
        workers.append(w)
    
    obs = []
    generator = DataGenerator(config_file, f'ob')
    for sink in generator.sinks:
        ob = Process(target=generator.observe, args=(sink,))
        ob.start()
        obs.append(ob)
    
    for ob in obs:
        ob.join()
    
    for w in workers:
        w.join()

class DataGenerator:
    def __init__(self, config, id):
        self.id = id
        self.config = config
        self.t = time.time()
        self.fake = Faker()
        self.t_unit = {
            's': 1,
            'ms': 1/1000,
            'us': 1/1000/1000,
            'ns': 1/1000/1000/1000
        }[self.config["precision"]]
        
        self.sinks_config = self.config["sinks"]
        self.sinks = self.create_sinks(self.sinks_config, self.config["fields"])
        
    def generate(self):
        for i in range(self.config["batch_size"]):
            self.t = self.t + self.t_unit
            yield self.generate_row()
            
    def generate_row(self):
        record = []
        for field in self.config["fields"]:
            record.append(self.generate_item(field))
        return record
    
    def generate_item(self, field):
        if field["type"] == 'date':
            return self.generate_date()
        
        if field["type"] == 'datetime':
            return self.generate_datetime()
        
        if field["type"] == 'timestamp':
            return self.generate_timestamp(precision=field["precision"])
        
        if field["type"] == 'number':
            return self.generate_number(format_string=field["format"])
        
        if field["type"] == 'string':
            return self.generate_string(format_string=field["format"])
        
        if field["type"] == 'worker_id':
            return self.id
    
    def generate_date(self):
        dt = datetime.fromtimestamp(self.t)
        return dt.strftime("%Y-%m-%d")
    
    def generate_datetime(self):
        dt = datetime.fromtimestamp(self.t)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_timestamp(self, precision="ms"):
        if self.config["realtime"]:
            t = time.time()
        else:
            t = self.t
            
        if precision == "s":
            return str(t)
        
        if precision == "ms":
            return str(t*1000)
        
        if precision == "us":
            return str(t*1000*1000)
        
        if precision == "ns":
            return str(t*1000*1000*1000)
    
    def generate_string(self, format_string="????"):
        return self.fake.bothify(text=format_string)
    
    def generate_number(self, format_string="####"):
        return self.fake.numerify(text=format_string)

    # shuffle the data to test insert with dis-ordered data
    def shuffle(self, data):
        result = [ x for x in data]
        random.shuffle(result)
        return result
    
    def csv(self):
        data = self.generate()
        result = ''
        for i in data:
            result = result + '|'.join(i) + '\n'
        return result
    
    def observe(self, sink):
        count = sink.count()
        start_time = time.time()
        while True:
            time.sleep(1)
            end_time = time.time()
            new_count = sink.count()
            count_diff = new_count - count
            time_diff = end_time - start_time
            print(f'iops for {sink.name} is {count_diff/time_diff}')
            if count_diff == 0:
                break;
            count = new_count
            start_time = end_time
    
    def load(self):
        for i in range(self.config["batch_number"]):
            for sink in self.sinks:
                query_latency = sink.send(self.csv())
                #print(f'data send to {sink.name} with {query_latency}')    
                
    def create_sinks(self, config, fields):
        sinks = []

        for t in config:
            if t["type"] == "kafka":
                sinks.append(KafkaSink(t,fields))
                
            if t["type"] == "console":
                sinks.append(ConsoleSink(t,fields))
                
            if t["type"] == "clickhouse":
                sinks.append(ClickhouseSink(t,fields))

            if t["type"] == "influx":
                sinks.append(InfluxSink(t,fields))
                
            # register customer sink here
        return sinks
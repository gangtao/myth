import time
import requests

from myth.sink import Sink

class InfluxSink(Sink):
    def __init__(self, config, fields, worker_id):
        Sink.__init__(self, config, fields, worker_id)
        self.config = config
        
        self.write_url = f'{self.config["url"]}write'
        self.query_url = f'{self.config["url"]}query'
        self.db = self.config["db"]
        self.measure = self.config["measure"]
        self.precision = self.config["precision"]
        self.tags = []
        self.fields = []
        
        self.timestamp_index = -1
        
        for i, v in enumerate(fields):
            if v["type"] == 'timestamp':
                self.timestamp_index = i
            elif v["type"] == 'number':
                field = {"name": v["name"], "index":i }
                self.fields.append(field)
            else:
                tag = {"name": v["name"], "index":i }
                self.tags.append(tag)
        
    def write(self, line):
        params = {'db': self.db}
        return requests.post(self.write_url, params=params, data = line)

    def query(self, fluxql):
        params = {'db': self.db, 'pretty':'true', 'q':fluxql}
        return requests.post(self.query_url, params=params)
        
    def send(self, data):
        line = ''
        for i in data.strip().split('\n'):  
            row = i.split('|')
            measure = self.measure 
            fields = ",".join([ f'{field["name"]}={row[field["index"]] }'  for field in self.fields])
            tags = ",".join([ f'{tag["name"]}={row[tag["index"]].replace(" ","")}'  for tag in self.tags])
            timestamp = int(float(row[self.timestamp_index]))
            
            line = line + f'{measure},{tags} {fields} {timestamp}' + '\n'
        
        ts = time.time() 
        r = self.write(line)
        te = time.time() 
        return te-ts
        
    
    def count(self):
        query = f'select count(*) from {self.measure}'

        r = self.query(query)
        result = r.json()
        result_count = result['results'][0]['series'][0]['values'][0][1]

        print('result count', result_count)

        if result_count:
            return int(result_count)
        else:
            return 0

class Influx2Sink(Sink):
    def __init__(self, config, fields, worker_id):
        Sink.__init__(self, config, fields, worker_id)
        self.config = config
        
        self.write_url = f'{self.config["url"]}api/v2/write'
        self.query_url = f'{self.config["url"]}api/v2/query'
        self.org = self.config["org"]
        self.bucket = self.config["bucket"]
        self.name = f'influx:{self.org}:{self.bucket}'
        self.token = self.config["token"]
        self.measure = self.config["measure"]
        self.precision = self.config["precision"]
        self.tags = []
        self.fields = []
        
        self.timestamp_index = -1
        
        for i, v in enumerate(fields):
            if v["type"] == 'timestamp':
                self.timestamp_index = i
            elif v["type"] == 'number':
                field = {"name": v["name"], "index":i }
                self.fields.append(field)
            else:
                tag = {"name": v["name"], "index":i }
                self.tags.append(tag)
        
    def write(self, line):
        headers = {'Authorization' : f'Token {self.token}'}
        params = {'org': self.org, 'bucket': self.bucket, 'precision': self.precision}
        return requests.post(self.write_url, headers=headers, params=params, data = line)

    def query(self, flux):
        headers = {'Authorization' : f'Token {self.token}'}
        params = {'org': self.org}
        data = {}
        data["type"] = "flux"
        data["query"] = flux
        return requests.post(self.query_url, headers=headers, params=params, json = data)
        
    def send(self, data):
        line = ''
        for i in data.strip().split('\n'):  
            row = i.split('|')
            measure = self.measure 
            fields = ",".join([ f'{field["name"]}={row[field["index"]] }'  for field in self.fields])
            tags = ",".join([ f'{tag["name"]}={row[tag["index"]].replace(" ","")}'  for tag in self.tags])
            timestamp = int(float(row[self.timestamp_index]))
            
            line = line + f'{measure},{tags} {fields} {timestamp}' + '\n'
        
        ts = time.time() 
        r = self.write(line)
        te = time.time() 
        return te-ts
        
    
    def count(self):
        query = f'''
            from(bucket: "{self.bucket}")
            |> range(start: -2d)
            |> group(columns: ["_measurement"])
            |> filter(fn: (r) =>
                r["_measurement"] == "{self.measure}" and
                r["_field"] == "{self.fields[0]["name"]}"
            )
            |> count()
            |> yield()
            '''

        r = self.query(query)
        result = r.text
        result_row = result.split('\n')[1]
        result_count = result_row.split(',')[-1]

        print('result count', result_count)

        if result_count:
            return int(result_count)
        else:
            return 0
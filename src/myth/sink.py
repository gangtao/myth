import socket
import time
import requests

from confluent_kafka import Producer
from faker import Faker


fake = Faker()

def is_number(n):
    is_number = True
    try:
        num = float(n)
        # check for "nan" floats
        is_number = num == num   # or use `math.isnan(num)`
    except ValueError:
        is_number = False
    return is_number


class Sink:
    def __init__(self, config, fields):
        self.config = config
        self.fields = fields
        self.name = 'sink'
        
    def send(self, data):
        print(data)
    
    def init(self, config):
        pass
    
    def name(self):
        return self.name
        
class KafkaSink(Sink):
    def __init__(self, config, fields):
        Sink.__init__(self, config, fields)
        self.kafka_config = {'bootstrap.servers': self.config["broker"], 
                'client.id': socket.gethostname()
            }
        self.topic_name = self.config["topic"]
        self.producer = Producer(self.kafka_config)
        self.name = f'kafka:{self.config["broker"]}'
        
    
    def send(self, data): 
        ts = time.time() 
        self.producer.produce(self.topic_name, key=fake.lexify(), value=data)
        self.producer.flush()
        te = time.time() 
        return te-ts
        
        
class ConsoleSink(Sink):
    def __init__(self, config, fields):
        Sink.__init__(self, config, fields)
        

class ClickhouseSink(Sink):
    def __init__(self, config, fields):
        Sink.__init__(self, config, fields)
        self.url = self.config["url"]
        
        self.schema_config = self.config["schema"]
        self.db = self.schema_config["database_name"]
        self.table = self.schema_config["table_name"]
        
        if self.schema_config["create_table"] == "auto":
            self.create_table = True
            self.create_table_sql = self.generate_schema()
        elif self.schema_config["create_table"] == "yes" :
            self.create_table = True
            self.create_table_sql = self.schema_config["create_table_sql"]
        else:
            self.create_table = False
            
        self.name = f'clickhouse:{self.config["url"]}'
            
        self.init()
        
    def send(self, data):
        load_sql = f'INSERT INTO {self.db}.{self.table} VALUES '
        rows=data.strip().split('\n')
        for row in rows:
            fields = row.split('|')
            processed_fields = self.process_fields(fields)
            load_sql = load_sql + '(' + ','.join(processed_fields) + ') '
        
        #print(load_sql)
        ts = time.time() 
        r = self.query(load_sql)
        te = time.time() 
        return te-ts
    
    def process_fields(self, fields):
        processed_fields = []
        for t,v in zip(self.fields_types, fields):
            if t == 'Float32':
                processed_fields.append(v)
            elif t.startswith('DateTime') and is_number(v):
                processed_fields.append(v)
            else:
                # adding ' for no number
                processed_fields.append(f"'{v}'")
        return processed_fields 
    
    def init(self):
        sql_create_db = f'CREATE DATABASE IF NOT EXISTS {self.db}'
        r = self.query(sql_create_db)
        
        if self.create_table:
            #print(self.create_table_sql)
            r = self.query(self.create_table_sql)
            #print(r.text)
            
    def generate_schema(self):
        sql_create_table = f'CREATE TABLE IF NOT EXISTS {self.db}.{self.table} ( '
        fields = [ f'{field["name"]} {self.get_db_type(field["type"])}' for field in self.fields]
        self.fields_types = [ self.get_db_type(field["type"]) for field in self.fields]
        sql_create_table = sql_create_table + ','.join(fields)
        sql_create_table = sql_create_table + ') ENGINE = MergeTree() PARTITION BY toYYYYMMDD(time) ORDER BY time'
        return sql_create_table
    
    def get_db_type(self, field): 
        if field == "date" :
            return "Date"
        
        if field == "datetime" :
            return "DateTime('UTC')"
            
        if field == "timestamp" :
            return "DateTime('UTC')"
            
        if field == "number" :
            return "Float32"
            
        if field == "string" :
            return "String"
        
        return "String"
    
    def query(self, sql):
        return requests.post(self.url, data = sql)
        
    def clean(self):        
        sql_drop_db = f'DROP DATABASE IF EXISTS {self.table}'
        r = self.query(sql_drop_db)
        print(r.text)
    
    def count(self):
        sql_count_table = f'SELECT COUNT(*) FROM {self.db}.{self.table}'
        r = self.query(sql_count_table)
        result = r.text
        print(result)
        return int(result)
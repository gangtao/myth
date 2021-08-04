import socket
import time
import requests

from confluent_kafka import Producer
from faker import Faker

fake = Faker()

class Sink:
    def __init__(self, config, fields, worker_id):
        self.config = config
        self.fields = fields
        self.name = 'sink'
        self.worker_id = worker_id
        
    def send(self, data):
        print(data)
    
    def init(self, config):
        pass
    
    def name(self):
        return self.name
        
class KafkaSink(Sink):
    def __init__(self, config, fields, worker_id):
        Sink.__init__(self, config, fields, worker_id)
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
        


import time
import socket
import requests
import json

from myth.sink import Sink

class QuestDBSink(Sink):
    def __init__(self, config, fields, worker_id):
        Sink.__init__(self, config, fields, worker_id)
        self.config = config
        self.name = 'questdb'
        
        self.host = f'{self.config["host"]}'
        self.port = int(self.config["port"])
        self.query_url = f'http://{self.config["host"]}:9000/exec'
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

        
    def write(self, lines):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.host, self.port))
            sock.sendall((lines).encode())            
        except socket.error as e:
            print("Got error: %s" % (e))

        sock.close()

    def query(self, sql):
        try:
            response = requests.post(self.query_url, params={'query': sql})
            return response.json()['dataset']
        except requests.exceptions.RequestException as e:
            print("Error: %s" % (e))
        
    def send(self, data):
        line = ''
        for i in data.strip().split('\n'):  
            row = i.split('|')
            measure = self.measure 
            fields = ",".join([ f'{field["name"]}={row[field["index"]] }'  for field in self.fields])
            tags = ",".join([ f'{tag["name"]}={row[tag["index"]].replace(" ","")}'  for tag in self.tags])
            # TODO : support different time unit, now it is bind from ms to ns
            timestamp = int(float(row[self.timestamp_index])*1000*1000)
            
            line = line + f'{measure},{tags} {fields} {timestamp}' + '\n'
        
        ts = time.time() 
        #print(line)
        r = self.write(line)
        te = time.time() 
        return te-ts
        
    
    def count(self):
        count_sql = f'select count(*) from {self.measure}'
        try:
            r = self.query(count_sql)
            print(r[0][0])
            return int(r[0][0])
        except:
            return 0

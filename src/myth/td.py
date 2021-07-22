import time
import requests
from requests.auth import HTTPBasicAuth

from myth.sink import Sink

class TDSink(Sink):
    def __init__(self, config, fields, worker_id):
        Sink.__init__(self, config, fields, worker_id)
        self.config = config
        self.name = 'tdengine'

        self.query_url = f'{self.config["url"]}rest/sql'
        # manually create user in taos is required
        # CREATE USER <user_name> PASS <'password'>;
        self.auth = HTTPBasicAuth(self.config["username"], self.config["password"])
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

        self.init()

    def query(self, sql):
        return requests.post(self.query_url, auth = self.auth, data = sql)

    def init(self):
        sql_create_db = f'CREATE DATABASE IF NOT EXISTS {self.db}'
        #print(sql_create_db)
        r = self.query(sql_create_db)
        #print(r.text)

        sql_create_stable = f'CREATE STABLE IF NOT EXISTS {self.db}.{self.measure} ( t TIMESTAMP '
        sql_create_stable = sql_create_stable + ', ' + ','.join([ f'{f["name"]} FLOAT ' for f in self.fields]) + ')'
        sql_create_stable = sql_create_stable + ' TAGS (' + ','.join([ f'{t["name"]} BINARY(64) ' for t in self.tags] )
        sql_create_stable = sql_create_stable + ')' 
        
        #print(sql_create_stable)
        r = self.query(sql_create_stable)
        #print(r.text)

    def clean(self):
        sql_drop_db = f'DROP DATABASE IF EXISTS {self.db}'
        r = self.query(sql_drop_db)
        print(r.text)
        
    def send(self, data):
        load_sql = f'INSERT INTO'

        for i in data.strip().split('\n'):  
            row = i.split('|')
            fields = ",".join([ f'{row[field["index"]]}'  for field in self.fields])
            tags = ",".join([ f'\"{row[tag["index"]].replace(" ","")}\"'  for tag in self.tags])
            timestamp = int(float(row[self.timestamp_index]))

            # split into different tables using worker id
            load_sql = load_sql + f' {self.db}.{self.worker_id} USING {self.db}.{self.measure} ' 
            load_sql = load_sql + ' TAGS ' + '(' + tags + ') '
            load_sql = load_sql + ' VALUES ' +  '(' + str(timestamp) + ' , ' + fields + ')'

        #print(load_sql)
        ts = time.time() 
        r = self.query(load_sql)
        te = time.time() 
        #print(r.text)
        return te-ts
    
    def count(self):
        count_sql = f'SELECT COUNT(*) FROM {self.db}.{self.measure} '
        r = self.query(count_sql)
        result = r.json()
        try:
            result_count = result["data"][0][0]
            return int(result_count)
        except:
            return 0
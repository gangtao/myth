import psycopg2 as pg
import datetime as dt
import time

from myth.sink import Sink

class MaterializeSink(Sink):
    def __init__(self, config, fields, worker_id):
        Sink.__init__(self, config, fields, worker_id)
        self.host = self.config["host"]
        self.port = self.config["port"]
        self.user = self.config["user"]
        self.password = self.config["password"]
        
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
            self.generate_schema()
            
        self.name = f'timescale:{self.host}'
        self.init()

    def write(self, sql):
        try:
            connection = pg.connect(user=self.user,
                                    password=self.password,
                                    host=self.host,
                                    port=self.port,
                                    dbname=self.db)
            cursor = connection.cursor()
            cursor.execute(sql)
            connection.commit()
        finally:
            if (connection):
                cursor.close()
                connection.close()

    def query(self, sql):
        try:
            connection = pg.connect(user=self.user,
                                    password=self.password,
                                    host=self.host,
                                    port=self.port,
                                    dbname=self.db)
            cursor = connection.cursor()
            cursor.execute(sql)
            records = cursor.fetchall()
            '''
            for row in records:
                print(row)
            '''
        finally:
            if (connection):
                cursor.close()
                connection.close()
                #print("Postgres connection is closed")
        return records
    
    def init(self):        
        if self.create_table:
            #print(self.create_table_sql)
            r = self.write(self.create_table_sql)
        
    def send(self, data):
        load_sql = f'INSERT INTO {self.table} VALUES '
        rows=data.strip().split('\n')
        for row in rows:
            fields = row.split('|')
            processed_fields = self.process_fields(fields)
            load_sql = load_sql + ' (' + ','.join(processed_fields) + ') ,'
        load_sql = load_sql[:-1]
        #print(load_sql)
        ts = time.time() 
        r = self.write(load_sql)
        te = time.time() 
        return te-ts
    
    def get_db_type(self, field): 
        if field == "date" :
            return "date"
        
        if field == "datetime" :
            return "TIMESTAMP WITHOUT TIME ZONE"
            
        if field == "timestamp" :
            return "double PRECISION"
            
        if field == "number" :
            return "double PRECISION"
            
        if field == "string" :
            return "text"
        
        return "text"
    
    def process_fields(self, fields):
        processed_fields = []
        for t,v in zip(self.fields_types, fields):
            if t.startswith('double'):
                processed_fields.append(v)
            elif t == 'TIMESTAMP WITHOUT TIME ZONE  NOT NULL':
                timestamp = float(v)/1000
                processed_fields.append(f'to_timestamp({timestamp})')  ## todo, this is for ms, need convert by precision
            else:
                # adding ' for no number
                processed_fields.append(f"'{v}'")
        return processed_fields 
            
    def generate_schema(self):
        sql_create_table = f'CREATE TABLE {self.table} ( '
        fields = [ f'{field["name"]} {self.get_db_type(field["type"])}' for field in self.fields]
        self.fields_types = [ self.get_db_type(field["type"]) for field in self.fields]
        sql_create_table = sql_create_table + ','.join(fields)
        sql_create_table = sql_create_table + ')'
        return sql_create_table
        
    def clean(self):        
        sql_drop_db = f'DROP DATABASE IF EXISTS {self.table}'
        r = self.query(sql_drop_db)
        print(r.text)
    
    def count(self):
        sql_count_table = f'SELECT COUNT(*) FROM {self.table}'
        r = self.query(sql_count_table)
        result_count = int(r[0][0])
        return result_count
import time

from myth.sink_factory import create_sink

class Executor:
    def __init__(self, config, id):
        self.id = id
        self.config = config
        
        self.sink_config = self.config["sink"]
        self.execute_config = self.config["execute"]
        self.sink = create_sink(self.sink_config, self.config["fields"], self.id)
        
    def execute(self):
        repeat = self.execute_config["repeat"]
        queries = self.execute_config["queries"]
        for query in queries:
            print(query["value"])
            start_time = time.time()
            for i in range(repeat):
                self.sink.query(query["value"])
            end_time = time.time()
            average_time = (end_time-start_time)/repeat
            print(f'query {query["name"]} took {average_time}')
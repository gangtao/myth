import json
from myth.generator import DataGenerator

def test():
    with open('clickhouse.json') as f:
        config = json.load(f) 
        m = DataGenerator(config, 'id')
        m.load()
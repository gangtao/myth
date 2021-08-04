from myth.sink import KafkaSink, ConsoleSink
from myth.clickhouse import ClickhouseSink
from myth.influx import InfluxSink, Influx2Sink
from myth.td import TDSink
from myth.questdb import QuestDBSink
from myth.timescale import TimeScaleSink

def create_sink(config, fields, worker_id):

    if config["type"] == "kafka":
        return KafkaSink(config,fields,worker_id)
        
    if config["type"] == "console":
        return ConsoleSink(config,fields,worker_id)
        
    if config["type"] == "clickhouse":
        return ClickhouseSink(config,fields,worker_id)

    if config["type"] == "influx":
        return InfluxSink(config,fields,worker_id)

    if config["type"] == "influx2":
        return Influx2Sink(config,fields,worker_id)

    if config["type"] == "tdengine":
        return TDSink(config,fields,worker_id)
    
    if config["type"] == "questdb":
        return QuestDBSink(config,fields,worker_id)
    
    if config["type"] == "timescale":
        return TimeScaleSink(config,fields,worker_id)
            
    # register customer sink here
    return None
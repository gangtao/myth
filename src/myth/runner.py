from multiprocessing import Process

from myth.generator import DataGenerator
from myth.executor import Executor

def run(config_file, worker_number, executor_number):
    print(config_file, worker_number)

    # start observation first
    generator = DataGenerator(config_file, f'ob')
    sink = generator.sink
    initial_count = sink.count()
    print(f'initial count is {initial_count}')
    ob = Process(target=generator.observe, args=(sink,initial_count,worker_number))
    ob.start()

    # start generator workers
    workers = []
    for i in range(worker_number):
        generator = DataGenerator(config_file, f'worker{i}')
        print(f'create {i} worker for write data')
        w = Process(target=generator.load)
        w.start()
        workers.append(w)
    
    ob.join()
    
    for w in workers:
        w.join()

    # start execute all queries
    executors = []
    for i in range(executor_number):
        executor = Executor(config_file, f'executor{i}')
        print(f'create {i} executor for query data')
        e = Process(target=executor.execute)
        e.start()
        executors.append(w)

    for e in executors:
        e.join()
    
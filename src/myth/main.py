import click
import json

from myth.runner import run

@click.command()
@click.option('--option', default='load', help='load|query')
@click.option('--config', default='generator.json', help='configuration file path')
@click.option('--worker', default=8, help='number of concurrent worker to load the data')
@click.option('--executor', default=1, help='number of concurrent executor to run the query')
def myth(option, config, worker, executor):
    with open(config) as f:
        config_file = json.load(f) 
        run(config_file, worker, executor)

if __name__ == '__main__':
    myth()
import click
import json
from myth.generator import generate_concurrent

@click.command()
@click.option('--option', default='load', help='load|query')
@click.option('--config', default='generator.json', help='configuration file path')
@click.option('--worker', default=8, help='number of concurrent worker')
def myth(option, config, worker):
    with open(config) as f:
        config_file = json.load(f) 
        generate_concurrent(config_file, worker)

if __name__ == '__main__':
    myth()
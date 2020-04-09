#!/usr/bin/python3
import argparse
import configparser
from subprocess import Popen
from config import Config
from shutil import rmtree
from os import mkdir, kill, unlink
from signal import SIGTERM
from os.path import exists
import json


def run_binary(path, home, action, shards=None, validators=None, non_validators=None, boot_nodes=None, output=None):
    command = [path, '--home', home, action]
    if shards:
        command.extend(['--shards', str(shards)])
    if validators:
        command.extend(['--v', str(validators)])
    if non_validators:
        command.extend(['--n', str(non_validators)])
    if boot_nodes:
        command.extend(['--boot-nodes', boot_nodes])

    if output:
        stdout = open(f'{output}.out', 'w')
        stderr = open(f'{output}.err', 'w')
    else:
        stdout = None
        stderr = None

    return Popen(command, stdout=stdout, stderr=stderr)


def run(config: Config):
    if config.overwrite:
        if config.path.exists():
            print("Removing old data.")
            rmtree(config.path)

    if not config.path.exists():
        run_binary(config.binary, config.path,
                   'testnet', shards=config.shards, validators=config.num_nodes).wait()

    # Edit config files
    for i in range(0, config.num_nodes):
        config_json = config.path / f'node{i}' / 'config.json'
        with open(config_json, 'r') as f:
            data = json.load(f)
        data['rpc']['addr'] = f'0.0.0.0:{3030 + i}'
        data['network']['addr'] = f'0.0.0.0:{24567 + i}'
        with open(config_json, 'w') as f:
            json.dump(data, f, indent=2)

    # Load public key from first node
    with open(config.path / f'node0' / 'node_key.json', 'r') as f:
        data = json.load(f)
        pk = data['public_key']

    # Recreate log folder
    rmtree('logs', ignore_errors=True)
    mkdir('logs')

    # Spawn network
    pid_fd = open('node.pid', 'w')
    for i in range(0, config.num_nodes):
        proc = run_binary(config.binary, config.path / f'node{i}', 'run',
                          boot_nodes=f'{pk}@127.0.0.1:24567' if i > 0 else None, output=f'logs/node{i}')
        print(proc.pid, file=pid_fd)
    pid_fd.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='config.ini')
    parser.add_argument('-k', '--stop', default=False, action='store_true')

    args = parser.parse_args()

    path = 'node.pid'

    if args.stop:
        if exists(path):
            with open(path) as f:
                for x in f.readlines():
                    pid = int(x.strip(' \n'))
                    print("Killing:", pid)
                    kill(pid, SIGTERM)
            unlink(path)

    else:
        if exists(path):
            print("There is already a test running. Stop it using:")
            print("python3 start_localnet.py -k")
            print("If this is a mistake, remove node.pid")
            exit(1)

        config = configparser.ConfigParser()
        config.read(args.config)
        config = Config(config)
        run(config)

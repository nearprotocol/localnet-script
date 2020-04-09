from pathlib import Path


class Config:
    def __init__(self, config):
        self.config = config

    @property
    def launch(self):
        return self.config['launch']

    @property
    def binary(self):
        return Path(self.launch['binary']).expanduser()

    @property
    def overwrite(self):
        return self.launch['overwrite'].lower() == 'true'

    @property
    def path(self):
        return Path(self.launch['path']).expanduser()

    @property
    def num_nodes(self):
        return int(self.launch['num_nodes'])

    @property
    def shards(self):
        return int(self.launch['shards'])

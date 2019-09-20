import os

import yaml

import environment


class Board(object):
    def __init__(self, target):

        self._config = None

        path = os.path.join(environment.env['paths']['configs'], 'boards')
        for (_, _, files) in os.walk(path):
            for file in files:
                with open(os.path.join(path, file), 'r') as f:
                    cfg = yaml.full_load(f.read())
                try:
                    for t in cfg['boards']:
                        if target.lower() in t.lower():
                            self._config = cfg
                            self._name = t
                        break
                except KeyError:
                    continue

        if self._config is None:
            raise Exception("Target \'{}\' not found in configuration files!".format(target))


    def __str__(self):
        return self._name



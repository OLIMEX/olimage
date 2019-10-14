import os
import yaml

import olimage.environment as env

from .parser import LoaderBase


class Variant(object):
    def __init__(self, name, data) -> None:
        self._name = name
        self._data = data

    def __str__(self) -> str:
        return self._name

    @property
    def id(self) -> int:
        return int(self._data['id'])

    @property
    def fdt(self) -> str:
        return self._data['fdt']

    @property
    def overlays(self) -> list:
        return self._data['overlays']


class Board(object):
    def __init__(self, name, data) -> None:
        self._name = name
        self._data = data

        # Create variants
        self._variants = []
        for key, value in data['variants'].items():
            self._variants.append(Variant(key, value))

    def __str__(self) -> str:
        return self._name

    @property
    def arch(self) -> str:
        return self._data['arch']

    @property
    def variants(self) -> list:
        return self._variants


class Boards(LoaderBase):
    def __init__(self) -> None:
        # Hold boards
        self._objects = []

        # Walk through boards directory
        path = os.path.join(env.paths['configs'], 'boards')

        for (_, _, files) in os.walk(path):
            for file in files:
                with open(os.path.join(path, file), 'r') as f:
                    try:
                        # Generate objects
                        data = yaml.full_load(f.read())['boards']
                        self._objects.append(Board(file.split('.')[0], data))
                    except KeyError:
                        continue

    def get_board(self, name: str) -> Board:
        for board in self._objects:
            if name.lower() in [str(x).lower() for x in board.variants]:
                return board

        raise Exception("No such board: \"{}\"".format(name))
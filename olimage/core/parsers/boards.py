import os
import yaml

import olimage.environment as env

from .parser import (LoaderBase, Parser)


class BoardPackage(Parser):
    @property
    def data(self):
        return self._data


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
        overlays = self._data['overlays']
        if overlays is None:
            return []
        else:
            return overlays



class Board(object):
    def __init__(self, name, data) -> None:
        self._name = name
        self._data = data

        # Create variants
        self._default = None
        self._variants = []
        for key, value in data['variants'].items():
            self._variants.append(Variant(key, value))

        # Create board packages
        self._board_packages = []
        for key, value in data['board_packages'].items():
            self._board_packages.append(BoardPackage(key, value))

    def __str__(self) -> str:
        return self._name

    def get_board_package(self, name: str) -> BoardPackage:
        for package in self._board_packages:
            if name == str(package):
                return package

        raise Exception("No such package: \"{}\"".format(name))

    @property
    def arch(self) -> str:
        return self._data['arch']

    @property
    def variants(self) -> [Variant]:
        return self._variants

    @property
    def board_packages(self) -> list:
        return self._board_packages

    @property
    def default(self) -> Variant:
        return self._default

    @default.setter
    def default(self, variant):
        self._default = variant


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
            for variant in board.variants:
                if name.lower() == str(variant).lower():
                    board.default = variant
                    return board

        raise Exception("No such board: \"{}\"".format(name))
import os
import yaml

import olimage.environment as env

from olimage.core.parsers.parser import (LoaderBase)
from . import (Board)


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
            for model in board.models:
                if name.lower() == str(model).lower():
                    board.target = model
                    return board

        raise Exception("No such board: \"{}\"".format(name))

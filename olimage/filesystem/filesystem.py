import os
import shutil

import olimage.environment as env
from olimage.core.parsers import Board
from olimage.core.parsers.packages import ParserPackages


class FileSystemBase(object):
    variant = None

    def __init__(self):
        """
        Initialize build directory and post-archive names
        """
        release = env.options['release']
        board: Board = env.objects['board']

        self._build_dir = os.path.join(env.paths['filesystem'], "{}-{}-{}".format(board.arch, release, self.variant))

        env.paths['build'] = self._build_dir
        env.objects['variant'] = ParserPackages().get_variant(self.variant)

    def _prepare_build_dir(self) -> None:
        """
        Remove previous build directory and create
        a new empty one

        :return: None
        """
        if os.path.exists(self._build_dir):
            shutil.rmtree(self._build_dir)
        os.mkdir(self._build_dir)
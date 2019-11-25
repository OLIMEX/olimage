import logging

import olimage.environment as env

from .shell import Shell

logger = logging.getLogger(__name__)


class Install(object):
    @staticmethod
    def __call__(files, mode='644'):
        if not isinstance(files, list):
            files = [files]

        for file in files:
            source = env.paths['overlay'] + file
            destination = env.paths['debootstrap'] + file

            logger.info("Installing {} to {} with permissions {}".format(source, destination, mode))
            Shell.run('install -D -v -m {} {} {}'.format(mode, source, destination))
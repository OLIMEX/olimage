import logging

import olimage.environment as env

from .shell import Shell

logger = logging.getLogger(__name__)


class Packagelist(object):
    @staticmethod
    def __call__(destination=None):
        source = env.paths['build'] + '/packages.list'
        Shell.chroot("/bin/bash -c 'dpkg -l > /packages.list'")
        Shell.run('mv {} {}'.format(source, destination))

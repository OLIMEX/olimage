import os

import olimage.environment as env

from olimage.core.utils import Utils


class Getty(object):
    @staticmethod
    def __call__(path: str):
        file = "/etc/systemd/system/getty@tty1.service.d/noclear.conf"
        source = env.paths['overlay'] + file
        destination = path + file

        # Install files
        Utils.shell.chroot('install -d "{}"'.format(os.path.dirname(file)), path)
        Utils.shell.run('install -m 644 {} {}'.format(source, destination))

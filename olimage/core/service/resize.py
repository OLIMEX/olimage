import os

import olimage.environment as env

from olimage.core.utils import Utils


class Resize(object):
    @staticmethod
    def install(path: str) -> None:
        files = [
            'usr/lib/olinuxino/olimex-expand',
            'etc/systemd/system/olinuxino-expand.service'
        ]

        for file in files:
            source = os.path.join(env.paths['overlay'], file)
            destination = os.path.join(path, file)

            if not os.path.exists(os.path.dirname(destination)):
                os.mkdir(os.path.dirname(destination))

            # Copy file
            # TODO: User install -m
            Utils.shell.run("rsync -rlDHWXhv {} {}".format(source, destination))

        # Make executable
        # TODO: Remove this
        Utils.shell.chroot("chmod +x /usr/lib/olinuxino/olinuxino-expand", path)

        # Enable service
        Utils.shell.chroot("systemctl enable olinuxino-expand.service", path)
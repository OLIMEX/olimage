from olimage.core.utils import Utils

from .base import SetupAbstract


class SetupUser(SetupAbstract):
    def setup(self, username, password, groups=None):
        # Root user is always present. Only change password for it.
        if username == 'root':
            Utils.shell.chroot(
                "/bin/bash -c '(echo {}; echo {};) | passwd root'".format(password, password),
                ignore_fail=True
            )
        else:
            Utils.shell.chroot(
                "/bin/bash -c '(echo {}; echo {};) | adduser --gecos {} {}'".format(
                    password, password, username, username
                ),
                ignore_fail=True
            )

        if groups:
            if not isinstance(groups, list):
                groups = [groups]
            for group in groups:
                Utils.shell.chroot(
                    "/bin/bash -c 'usermod -a -G {} {}'".format(group, username),
                    ignore_fail=True
                )

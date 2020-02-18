import olimage.environment as env

from .shell import Shell as shell


class Systemctl(object):

    @staticmethod
    def enable(service: str):
        shell.chroot('systemctl enable {}'.format(service), env.paths['debootstrap'])

    @staticmethod
    def disable(service: str):
        shell.chroot('systemctl disable {}'.format(service), env.paths['debootstrap'])

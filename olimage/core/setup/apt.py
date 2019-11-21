import olimage.environment as env

from olimage.core.utils import Utils


class Apt(object):
    @staticmethod
    def __call__(release: str):

        file = '/etc/apt/sources.list.d/olimex.list'
        source = env.paths['overlay'] + file
        destination = env.paths['debootstrap'] + file

        # Install gnupg
        Utils.shell.chroot(
            'apt-get install -y gnupg',
            env.paths['debootstrap']
        )

        # Import gpg key
        Utils.shell.chroot(
            'apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 2BE33123120C50F2666530ED09271DCFB6350689',
            env.paths['debootstrap']
        )

        # Install source list
        Utils.shell.run("install -m 644 {} {}".format(source, destination))
        Utils.template.install(destination, release=release)

        # Update sources
        Utils.shell.chroot(
            'apt-get update',
            env.paths['debootstrap']
        )

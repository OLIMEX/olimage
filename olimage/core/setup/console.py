from olimage.core.utils import Utils


class Console(object):
    @staticmethod
    def __call__(path: str):

        # Configure
        Utils.shell.chroot(
            'echo "console-setup console-setup/charmap47 select UTF-8" | debconf-set-selections',
            path
        )
        Utils.shell.chroot(
            'echo "console-setup console-setup/codeset47 select Guess optimal character set" | debconf-set-selections',
            path
        )

        Utils.shell.chroot(
            'echo "console-setup console-setup/fontface47 select  Do not change the boot/kernel font" | debconf-set-selections',
            path
        )

        # Install locales
        Utils.shell.chroot(
            'apt-get install -y console-setup',
            path
        )

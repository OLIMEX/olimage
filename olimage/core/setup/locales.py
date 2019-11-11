from olimage.core.utils import Utils


class Locales(object):
    @staticmethod
    def __call__(path: str, locale: str):

        # Configure
        Utils.shell.chroot(
            'echo "locales locales/locales_to_be_generated multiselect ${} UTF-8" | debconf-set-selections'.format(locale),
            path
        )
        Utils.shell.chroot(
            'echo "locales locales/default_environment_locale select ${}" | debconf-set-selections'.format(locale),
            path
        )

        # Install locales
        Utils.shell.chroot(
            'apt-get install -y locales',
            path
        )

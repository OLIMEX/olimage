from olimage.core.utils import Utils


class Locales(object):
    @staticmethod
    def __call__(path: str, locale: str):

        # Configure
        Utils.shell.chroot(
            'bash -c \'\
            echo "locales locales/locales_to_be_generated multiselect {locale} UTF-8" | debconf-set-selections -v; \
            echo "locales locales/default_environment_locale select {locale}" | debconf-set-selections -v \
            \''.format(locale=locale),
            path
        )

        # Install
        Utils.shell.chroot('apt-get install -y locales', path)

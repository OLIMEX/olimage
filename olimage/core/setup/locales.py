from olimage.core.utils import Utils


class Locales(object):
    @staticmethod
    def __call__(path: str, locale: str):

        # Configure
        Utils.shell.chroot(
            'bash -c \'echo "locales locales/locales_to_be_generated multiselect {} UTF-8" | \
                debconf-set-selections -v\''.format(locale),
            path
        )

        Utils.shell.chroot(
            'bash -c \'echo "locales locales/default_environment_locale select {}" | \
                debconf-set-selections -v\''.format(locale),
            path
        )
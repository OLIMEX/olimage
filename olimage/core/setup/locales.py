import olimage.environment as env

from olimage.core.io import Console
from olimage.core.utils import Utils

from .base import SetupAbstract


class SetupLocales(SetupAbstract):
    def setup(self, locale: str):

        # Configure
        with Console("Generating locales: \'{}\'".format(locale)):
            Utils.shell.chroot(
                'bash -c \'\
                echo "locales locales/locales_to_be_generated multiselect {locale} UTF-8" | debconf-set-selections -v; \
                echo "locales locales/default_environment_locale select {locale}" | debconf-set-selections -v \
                \''.format(locale=locale),
                env.paths['build']
            )

        # Install
        with Console("Installing packages"):
            Utils.shell.chroot('apt-get install -y {}'.format(' '.join(self.packages)))

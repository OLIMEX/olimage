import olimage.environment as env

from olimage.core.utils import Utils

from .base import SetupAbstract


class SetupTimezone(SetupAbstract):
    def setup(self, timezone: str):
        file = '/etc/timezone'

        Utils.install(file)
        Utils.template.install(env.paths['build'] + file, timezone=timezone)

        # Reconfigure
        Utils.shell.chroot('dpkg-reconfigure -f noninteractive tzdata')

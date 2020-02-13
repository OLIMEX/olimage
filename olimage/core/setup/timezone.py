import olimage.environment as env

from olimage.core.utils import Utils


class SetupTimezone(object):
    @staticmethod
    def __call__(path: str, timezone: str):
        file = '/etc/timezone'

        Utils.install(file)
        Utils.template.install(
            path + file,
            timezone=timezone
        )

        # Reconfigure
        Utils.shell.chroot('dpkg-reconfigure -f noninteractive tzdata', path)

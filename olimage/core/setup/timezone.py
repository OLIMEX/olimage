import olimage.environment as env

from olimage.core.utils import Utils


class SetupTimezone(object):
    @staticmethod
    def __call__(timezone: str):
        file = '/etc/timezone'

        Utils.install(file)
        Utils.template.install(
            env.paths['build'] + file,
            timezone=timezone
        )

        # Reconfigure
        Utils.shell.chroot('dpkg-reconfigure -f noninteractive tzdata', env.paths['build'])

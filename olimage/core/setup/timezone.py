import olimage.environment as env

from olimage.core.utils import Utils


class Timezone(object):
    @staticmethod
    def __call__(path: str, timezone: str):

        file = '/etc/timezone'

        source = env.paths['overlay'] + file
        destination = path + file

        # Copy file
        Utils.shell.run("install -v -m 644 {} {}".format(source, destination))

        # Install template
        Utils.template.install(
            destination,
            timezone=timezone
        )

        # Reconfigure
        Utils.shell.chroot('dpkg-reconfigure -f noninteractive tzdata', path)

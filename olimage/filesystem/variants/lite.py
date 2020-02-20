import os

import olimage.environment as env

from olimage.core.io import Console
from olimage.core.parsers import Board, Distribution, Users
from olimage.core.parsers.packages.variant import Variant
from olimage.core.service import Service
from olimage.core.setup import Setup
from olimage.core.utils import Utils

from olimage.filesystem.filesystem import FileSystemBase
from olimage.filesystem.stamp import stamp


class FileSystemLite(FileSystemBase):
    variant = 'lite'

    @stamp
    def build(self):
        self._prepare_build_dir()

        # Built a new file system
        with Console("Running qemu-debootstrap"):
            # TODO: Store date, UUID and configs and compare them to the stamp
            board: Board = env.objects['board']
            distribution: Distribution = env.objects['distribution']
            release = env.options['release']

            Utils.qemu.debootstrap(
                arch=board.arch,
                release=release,
                path=self._build_dir,
                components=distribution.components,
                include=None,
                mirror=distribution.repository)

        # Compress
        with Console("Creating archive"):
            Utils.archive.gzip(self._build_dir, self._build_dir + '.build.tar.gz')

    @stamp
    def configure(self):
        self._prepare_build_dir()

        # Extract fresh copy
        with Console("Extracting archive"):
            Utils.archive.extract(self._build_dir + '.build.tar.gz', self._build_dir)

        # Configure apt
        with Console("Configuring the APT repositories"):
            if env.options['apt_cacher']:
                Service.apt_cache.enable(env.options['apt_cacher_host'], env.options['apt_cacher_port'])

            Setup.apt(env.options['release'])

        # Configure locales
        # NOTE: This must be run before package installation
        with Console("Configuring locales"):
            Setup.locales(env.options['locale'])

        # Configure console
        with Console("Configuring console"):
            Setup.console(env.options['keyboard_keymap'], env.options['keyboard_layout'])

        # Install packages
        with Console("Installing packages"):
            Utils.shell.chroot('apt-get install -y {}'.format(' '.join(env.objects['variant'].packages)))

        # Generate boot files
        with Console("Generating boot files"):
            Setup.boot()

        # Install kernel
        with Console("Installing kernel"):
            Utils.shell.chroot('apt-get install -y linux-image-5.5.2-olimex')

        # Configure hostname
        hostname = str(env.objects['board'])
        if env.options['hostname']:
            hostname = env.options['hostname']
        with Console("Configuring hostname: \'{}\'".format(hostname)):
            Setup.hostname(hostname)

        # Configure users
        with Console("Configuring users"):
            for user in Users():
                with Console("Adding user: \'{}\'".format(str(user))):
                    Setup.user(str(user), user.password, groups=user.groups)

        # Configure timezone
        with Console("Configuring timezone: \'{}\'".format(env.options['timezone'])):
            Setup.timezone(env.options['timezone'])

        with Console("Configuring services"):
            # Disable useless services
            for service in ['hwclock.sh', 'nfs-common', 'rpcbind']:
                with Console("Disabling: \'{}\'".format(service)):
                    Utils.systemctl.disable(service)

            # Enable the custom services
            for s in [Service.getty, Service.expand]:
                s.enable()

            if env.options['ssh']:
                Service.ssh.enable()
            else:
                Service.ssh.disable()

    @stamp
    def cleanup(self):
        with Console("APT sources"):
            if env.options['apt_cacher']:
                Service.apt_cache.disable()

            Utils.shell.chroot('apt-get clean')

    @stamp
    def export(self):
        with Console("Creating archive: {}".format(os.path.basename(self._build_dir) + '.tar.gz')):
            Utils.archive.gzip(self._build_dir)

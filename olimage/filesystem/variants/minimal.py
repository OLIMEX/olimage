import olimage.environment as env

from olimage.core.io import Console
from olimage.core.parsers import Board, Distribution, Users, NetworkParser, Interface
from olimage.core.service import Service
from olimage.core.setup import Setup
from olimage.core.utils import Utils

from olimage.filesystem.base import FileSystemBase
from olimage.filesystem.decorators import export, prepare, stamp


class VariantMinimal(FileSystemBase):
    stages = ['build', 'configure', 'cleanup']
    variant = 'minimal'

    @stamp
    @export
    @prepare
    def build(self):

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

            # Utils.shell.run("ls -laR --time-style='+' {}/ > 1.txt".format(self._build_dir), shell=True)

    @stamp
    @export
    @prepare
    def configure(self):

        # Copy resolv.conf
        with Console("Copying /etc/resolv.conf"):
            Utils.shell.run('rm -vf {}/etc/resolv.conf'.format(self._build_dir), ignore_fail=True)
            Utils.shell.run('cp -vf /etc/resolv.conf {}/etc/resolv.conf'.format(self._build_dir))

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
        self._install_packages()

        # Generate boot files
        with Console("Generating boot files"):
            Setup.boot()

        if env.objects['board'].arch == 'arm64':
            with Console("Installing ATF"):
                Utils.shell.chroot('apt-get install -y arm-trusted-firmware-olinuxino')

        # Install kernel
        with Console("Configuring kernel"):
            Setup.kernel()

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

        with Console("Configuring network"):
            Setup.network()

        with Console("Install additional files"):
            Setup.extra()

        with Console("Configuring services"):
            # Disable useless services
            for service in ['hwclock.sh', 'nfs-common', 'rpcbind']:
                with Console("Disabling: \'{}\'".format(service)):
                    Utils.systemctl.disable(service)

            # Enable the custom services
            for s in [Service.getty]:
                s.enable()

            if env.options['ssh']:
                Service.ssh.enable()
            else:
                Service.ssh.disable()

    @stamp
    @export(final=True)
    @prepare
    def cleanup(self):
        super().cleanup()

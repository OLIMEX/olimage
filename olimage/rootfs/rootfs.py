import logging
import os
import shutil

import olimage.environment as env

from olimage.core.parsers import (Boards, Board, Distributions, Images, Partitions, Users)
from olimage.core.service import Service
from olimage.core.setup import Setup
from olimage.core.stamp import rootfs_stamp
from olimage.core.utils import Utils
from olimage.core.printer import Printer


logger = logging.getLogger(__name__)


class Rootfs(object):
    def __init__(self, boards: Boards, distributions: Distributions, images: Images, users: Users, partitions: Partitions):

        # Initialize dependencies
        self._board: Board = boards.get_board(env.options['board'])
        self._distributions = distributions
        self._image = images.get_image(env.options['variant'])
        self._partitions = partitions
        self._users = users

        # Initialize module attributes
        self._distribution = None
        self._release = None

        # Check if release is valid
        release: str = env.options['release']

        for dist in self._distributions:
            if release == dist:
                self._distribution = dist
                self._release = dist.recommended
            if release in dist.releases:
                self._distribution = dist
                self._release = release

        if self._release is None:
            raise Exception("Target distribution \'{}\' not found in configuration files".format(release))

        # Store cleanup
        self._cleanup = []

        # Store variant
        self._variant = env.options['variant']

        # Set build path
        self._debootstrap = os.path.join(
            env.paths['rootfs'], "{}-{}".format(self._board.arch, self._release))
        self._archive = self._debootstrap + '.tar.gz'
        env.paths['debootstrap'] = self._debootstrap

    @Printer("Building")
    @rootfs_stamp
    def build(self):

        # Remove previous directory
        if os.path.exists(self._debootstrap):
            shutil.rmtree(self._debootstrap)
        os.mkdir(self._debootstrap)

        # Built a new rootfs
        Utils.qemu.debootstrap(
            arch=self._board.arch,
            release=self._release,
            path=self._debootstrap,
            components=self._distribution.components,
            include=None,
            mirror=self._distribution.repository)

        # Compress
        Utils.archive.gzip(self._debootstrap)

    @Printer("Configuring")
    @rootfs_stamp
    def configure(self):

        # Remove previous directory
        if os.path.exists(self._debootstrap):
            shutil.rmtree(self._debootstrap)
        os.mkdir(self._debootstrap)

        # Extract fresh copy
        Utils.archive.extract(self._archive, env.paths['rootfs'])

        # Configure apt
        if env.options['apt_cacher']:
            Service.apt_cache.install(env.options['apt_cacher_host'], env.options['apt_cacher_port'])
            self._cleanup.append(Service.apt_cache.uninstall)
        Setup.apt(self._release)
        self._cleanup.append(Setup.apt.clean)

        # Configure locales
        # NOTE: This must be run before package installation
        Setup.locales(self._debootstrap, env.options['locale'])

        # Configure console
        # NOTE: This must be run before package installation
        Setup.console(self._debootstrap, env.options['keyboard_keymap'], env.options['keyboard_layout'])

        # Install packages
        Utils.shell.chroot('apt-get install -y {}'.format(' '.join(self._image.packages)), self._debootstrap)

        # Configure getty
        Setup.getty(self._debootstrap)

        # Configure hostname
        hostname = str(self._board)
        if env.options['hostname']:
            hostname = env.options['hostname']
        Setup.hostname(hostname, self._debootstrap)

        # Configure users
        for user in self._users:
            Setup.user(str(user), user.password, self._debootstrap, groups=user.groups)

        # Configure timezone
        Setup.timezone(self._debootstrap, env.options['timezone'])

        # Disable useless services
        Utils.systemctl.disable('hwclock.sh')
        Utils.systemctl.disable('nfs-common')
        Utils.systemctl.disable('rpcbind')

        # Configure ssh
        Setup.ssh(self._debootstrap, env.options['ssh'])

        # # Install services
        # Service.resize.install()
        #
        # # Setup boot
        # # Note: This depends on olimex-sunxi-overlays
        # Setup.boot(self._board, self._partitions)

    @Printer("Installing services")
    @rootfs_stamp
    def services(self):
        # Install services
        Service.resize.install()

        # Setup boot
        # Note: This depends on olimex-sunxi-overlays
        Setup.boot(self._board, self._partitions)

    @Printer("Cleanup")
    def cleanup(self):
        # Cleanup registered functions
        for item in self._cleanup:
            item()

import logging
import os
import shutil

import olimage.environment as env

from olimage.core.io import Output
from olimage.core.parsers import (Boards, Distributions, Partitions, Variants, Users)
from olimage.core.parsers.boards import Board
from olimage.core.service import Service
from olimage.core.setup import Setup
from olimage.core.utils import Utils


from .stamp import stamp


class Rootfs(object):
    def __init__(self, boards: Boards, distributions: Distributions, variants: Variants, users: Users, partitions: Partitions):

        # Initialize dependencies
        self._board: Board = boards.get_board(env.options['board'])
        self._distributions = distributions
        self._variant = variants.get_variant(env.options['variant'])
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

        # Set build path
        self._debootstrap = os.path.join(
            env.paths['rootfs'], "{}-{}".format(self._board.arch, self._release))
        self._archive = self._debootstrap + '.tar.gz'
        env.paths['debootstrap'] = self._debootstrap

    @stamp
    def build(self):

        # Remove previous directory
        if os.path.exists(self._debootstrap):
            shutil.rmtree(self._debootstrap)
        os.mkdir(self._debootstrap)

        # Built a new rootfs
        with Output.step("Running qemu-debootstrap"):
            Utils.qemu.debootstrap(
                arch=self._board.arch,
                release=self._release,
                path=self._debootstrap,
                components=self._distribution.components,
                include=None,
                mirror=self._distribution.repository)

        # Compress
        with Output.step("Creating archive"):
            Utils.archive.gzip(self._debootstrap)

    @stamp
    def configure(self):

        # Remove previous directory
        if os.path.exists(self._debootstrap):
            shutil.rmtree(self._debootstrap)
        os.mkdir(self._debootstrap)

        # Extract fresh copy
        with Output.step("Extracting archive"):
            Utils.archive.extract(self._archive, env.paths['rootfs'])

        # Configure apt
        if env.options['apt_cacher']:
            Service.apt_cache.install(env.options['apt_cacher_host'], env.options['apt_cacher_port'])
            self._cleanup.append(Service.apt_cache.uninstall)
        with Output.step("Configuring the APT repositories"):
            Setup.apt(self._release)
            self._cleanup.append(Setup.apt.clean)

        # Configure locales
        # NOTE: This must be run before package installation
        with Output.step("Configuring locales"):
            Setup.locales(self._debootstrap, env.options['locale'])

        # Configure console
        # NOTE: This must be run before package installation
        with Output.step("Configuring console"):
            Setup.console(self._debootstrap, env.options['keyboard_keymap'], env.options['keyboard_layout'])

        # Install packages
        with Output.step("Installing packages"):
            pass
            # Utils.shell.chroot('apt-get install -y {}'.format(' '.join(self._variant.packages)), self._debootstrap)

        # Configure hostname
        hostname = str(self._board)
        if env.options['hostname']:
            hostname = env.options['hostname']
        with Output.step("Configuring hostname: \'{}\'".format(hostname)):
            Setup.hostname(hostname, self._debootstrap)

        # Configure users
        with Output.step("Configuring users"):
            for user in self._users:
                with Output.substep("Adding user: \'{}\'".str(user)):
                    Setup.user(str(user), user.password, self._debootstrap, groups=user.groups)

        # Configure timezone
        with Output.step("Configuring timezone: \'{}\'".env.options['timezone']):
            Setup.timezone(self._debootstrap, env.options['timezone'])

        # Disable useless services
        with Output.step("Removing useless services"):
            for service in ['hwclock.sh', 'nfs-common', 'rpcbind']:
                with Output.substep("Removing \'\'".format(service)):
                    Utils.systemctl.disable(service)

        # Configure ssh
        with Output.step("{}abling SSH".format('En' if env.options['ssh'] else 'Dis')):
            Setup.ssh(self._debootstrap, env.options['ssh'])

    @stamp
    def services(self):
        with Output.step("Installing services"):
            # Install services
            for s in [ Service.getty, Service.resize ]:
                with Output.substep("Enabling: \'{}\'".format(s.name())):
                    s.enable()

        # Setup boot
        # Note: This depends on olimex-sunxi-overlays
        # Setup.boot(self._board, self._partitions)

    def cleanup(self):
        # Cleanup registered functions
        for item in self._cleanup:
            item()

import logging
import os
import shutil

import olimage.environment as env

from olimage.core.parsers import (Boards, Board, Distributions, Images, Users)
from olimage.core.service import Service
from olimage.core.setup import Setup
from olimage.core.stamp import rootfs_stamp
from olimage.core.utils import Utils
from olimage.utils import Printer


logger = logging.getLogger(__name__)


class Rootfs(object):
    def __init__(self, boards: Boards, distributions: Distributions, images: Images, users: Users):

        # Initialize dependencies
        self._board: Board = boards.get_board(env.options['board'])
        self._distributions = distributions
        self._image = images.get_image(env.options['variant'])
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
            self._board.arch,
            self._release,
            self._debootstrap,
            self._distribution.components,
            None,
            self._distribution.repository)

        # Compress
        Utils.archive.gzip(self._debootstrap)

    @Printer("Configuring")
    @rootfs_stamp
    def configure(self):

        # Configure apt
        if env.options['apt_cacher']:
            Service.apt_cache.install(self._debootstrap, env.options['apt_cacher_host'], env.options['apt_cacher_port'])
            self._cleanup.append({
                'function': Service.apt_cache.uninstall,
                'args': [self._debootstrap]
            })

        # Configure locales
        Setup.locales(self._debootstrap, env.options['locale'])

        # Configure getty
        Setup.getty(self._debootstrap)

        return

        # Configure hostname
        Setup.hostname(str(self._board), self._debootstrap)



        # Setup all provided users
        for user in self._users:
            Setup.user(str(user), user.password, self._debootstrap, groups=user.groups)

        # Install services
        # Service.resize.install(self._debootstrap)


    @Printer("Cleanup")
    def cleanup(self):
        for item in self._cleanup:
            item['function'](*item['args'])

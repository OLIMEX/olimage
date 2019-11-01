import logging
import os
import shutil

import olimage.environment as env

from olimage.core.parsers import (Boards, Board, Distributions, Images, Users)
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

        # Store variant
        self._variant = env.options['variant']

        # Set build path
        self._rootfs = os.path.join(
            env.paths['workdir'], 'rootfs', "{}-{}".format(self._board.arch, self._release))
        env.paths['rootfs'] = self._rootfs

    @Printer("Building")
    @rootfs_stamp
    def build(self):

        # Remove previous directory
        if os.path.exists(self._rootfs):
            shutil.rmtree(self._rootfs)
        os.mkdir(self._rootfs)

        # Built a new rootfs
        Utils.qemu.debootstrap(
            self._board.arch,
            self._release,
            self._rootfs,
            self._distribution.components,
            self._image.packages,
            self._distribution.repository)

        # Compress
        Utils.archive.gzip(self._rootfs)

    @Printer("Configuring")
    @rootfs_stamp
    def configure(self):

        # Configure hostname
        Setup.hostname(str(self._board), self._rootfs)

        # Setup all provided users
        for user in self._users:
            Setup.user(str(user), user.password, self._rootfs, groups=user.groups)


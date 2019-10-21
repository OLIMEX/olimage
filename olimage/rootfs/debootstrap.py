import logging
import math
import os
import shlex
import shutil

import olimage.environment as env

from .utils.mount import Mounter, Map
from olimage.core.parsers import (Boards, Board, Distributions, Images, Partitions, Users)
from olimage.utils import Printer, RootFSStamper, Worker, Templater

logger = logging.getLogger(__name__)


class Debootstrap(object):
    def __init__(self,
                 boards: Boards, distributions: Distributions, images: Images, partitions: Partitions, users: Users):

        # Initialize dependencies
        self._board: Board = boards.get_board(env.options['board'])
        self._partitions = partitions
        self._distributions = distributions
        self._image = images.get_image(env.options['variant'])
        self._users = users

        # Initialize module attributes
        self._distribution = None
        self._release = None

        # Hold cleanup
        self._cleanup = []

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
            env.options['workdir'], 'rootfs', "{}-{}".format(self._board.arch, self._release))
        env.paths['rootfs'] = self._rootfs

        # Configure stamper
        self._stamper = RootFSStamper(os.path.join(env.options['workdir'], 'rootfs'))

        # Output image
        self._output_file = os.path.join(env.paths['workdir'], 'images', 'test4.img')
        env.paths['output_file'] = self._output_file

    def __del__(self):
        if hasattr(self, '_cleanup'):
            for f in reversed(self._cleanup):
                f()

    @Printer("Creating base system")
    def _qemu_debootstrap(self):
        """
        Create bare minimum rootfs

        :return: None
        """

        if 'debootstrap' in self._stamper.stamps and os.path.exists(self._rootfs):
            return self

        self._stamper.remove('debootstrap')
        if os.path.exists(self._rootfs):
            shutil.rmtree(self._rootfs)
        os.mkdir(self._rootfs)

        Worker.run(
            shlex.split("qemu-debootstrap --arch={} --components={} --include={} {} {} {}".format(
                self._board.arch,
                ",".join(self._distribution.components),
                ",".join(self._image.packages),
                self._release,
                self._rootfs,
                self._distribution.repository)),
            logger
        )
        self._stamper.stamp('debootstrap')

        return self

    def _install_overlay(self):
        """
        Copying overlay directory to target

        :return: self
        """
        logger.info("Installing rootfs overlay")
        Worker.run(shlex.split("rsync -rlDHWXhv {}/ {}/".format(env.paths['overlay'], self._rootfs), logger))

        return self

    def _set_hostname(self, hostname):
        """
        Prepare /etc/hostname and /ets/hosts

        :param hostname: board hostname
        :return: self
        """

        logger.info("Setting hostname to \"{}\"".format(hostname))
        Templater.install(
            [
                os.path.join(self._rootfs, f) for f in ['etc/hostname', 'etc/hosts']
            ],
            hostname=hostname
        )

        return self

    def _set_fstab(self):
        """
        Prepare /etc/fstab

        :return: self
        """

        for part in self._partitions:
            logger.debug("Adding {} as UUID={} to {}".format(part, part.fstab.uuid, part.fstab.mount))

        Templater.install(
            [
                os.path.join(self._rootfs, 'etc/fstab')
            ],
            partitions=[
                {
                    'uuid' : '{:36}'.format(part.fstab.uuid),
                    'mount' : '{:15}'.format(part.fstab.mount),
                    'type' : '{:7}'.format(part.fstab.type),
                    'options' : '{:8}'.format(part.fstab.options),
                    'dump' : '{:7}'.format(part.fstab.dump),
                    'pass' : '{:8}'.format(part.fstab.passno)
                } for part in self._partitions
            ]
        )

        return self

    def _set_users(self):

        for user in self._users:
            passwd = user.password

            # Assuming root user is always present
            if str(user) != "root":
                Worker.chroot(
                    shlex.split("/bin/bash -c '(echo {}; echo {};) | adduser --gecos {} {}'".format(passwd, passwd, user, user)),
                    self._rootfs,
                    logger,
                    ignore_fail = True
                )
            else:
                logger.debug("Adding user {} with passwd {}".format(user, passwd))
                Worker.chroot(
                    shlex.split("/bin/bash -c '(echo {}; echo {};) | passwd root'".format(passwd, passwd)),
                    self._rootfs,
                    logger)

                # Optionally permit root login
                if user.permit_login:
                    logger.debug("Permitting root login")

            # Check force password change
            if user.force_change:
                Worker.chroot(
                    shlex.split("/bin/bash -c 'chage -d 0 {}'".format(user)),
                    self._rootfs,
                    logger)

            # Add users to groups
            try:
                for group in user.groups:
                    Worker.chroot(
                        shlex.split("/bin/bash -c 'usermod -a -G {} {}'".format(group, user)),
                        self._rootfs,
                        logger)
            except AttributeError:
                pass

    @Mounter.mount()
    @Printer("Configuring")
    def configure(self):

        # Run configure steps
        self._install_overlay()
        self._set_fstab()
        self._set_hostname(str(self._board))

        if 'configured' in self._stamper.stamps:
            return self

        self._set_users()
        self._stamper.stamp('configured')

        return self

    def build(self):
        print("\nBuilding: \033[1m{}\033[0m based distribution".format(self._release))

        # Run build steps
        return self._qemu_debootstrap()

    @staticmethod
    def get_size(path):
        size = 0
        for dir, _, file in os.walk(path):
            for f in file:
                fp = os.path.join(dir, f)

                if not os.path.islink(fp):
                    size += os.path.getsize(fp)

        return size

    @Printer("Generating blank image")
    def generate(self):
        """
        Generate black image

        :return: self
        """

        # Get size and add 500MiB size
        size = math.ceil(self.get_size(self._rootfs)/1024/1024) + 500

        logger.info("Creating empty file: {} with size {}".format(self._output_file, size))

        Worker.run(
            shlex.split("qemu-img create -f raw {} {}M".format(self._output_file, size)),
            logger
        )

        return self

    @Mounter.map()
    @Printer("Formatting partitions")
    def format(self):

        # Create partitions
        for partition in self._partitions:
            logger.info("Formatting partition: {}".format(partition))

            # Get parted related information
            device = partition.device
            fstab = partition.fstab

            opts = ''
            if type == 'ext4':
                opts = '-O ^64bit,^metadata_csum'

            # Make filesystem
            Worker.run(shlex.split('mkfs.{} {} {}'.format(fstab.type, opts, device)), logger)
            Worker.run(shlex.split('udevadm trigger {}'.format(device)), logger)
            Worker.run(shlex.split('udevadm settle'.format(device)), logger)

            # Generate UUID
            fstab.uuid = Worker.run(
                shlex.split('blkid -s UUID -o value {}'.format(device)),
                logger
            ).decode().splitlines()[0]
            logger.debug("UUID: {}".format(fstab.uuid))

        return self

    @Printer("Creating partitions")
    def partition(self):
        """
        Partition the output blank image

        :return: self
        """

        # Create label
        logger.info("Creating disk label: msdos")
        Worker.run(
            shlex.split('parted -s {} mklabel msdos'.format(self._output_file)),
            logger
        )

        # Create partitions
        for part in self._partitions:
            logger.info("Creating partition: {}".format(part))
            Worker.run(
                shlex.split('parted -s {} mkpart primary {} {} {}'.format(
                    self._output_file,
                    part.parted.type,
                    part.parted.start,
                    part.parted.end
                )),
                logger
            )

        return self

    @Mounter.mount()
    @Printer("Copying to raw image")
    def copy(self):
        exclude = ['/dev/*', '/proc/*', '/run/*', '/tmp/*', '/sys/*']
        order = []

        for part in self._partitions:

            mount = part.fstab.mount
            if mount == '/':
                order.insert(0, mount)
            else:
                order.append(mount)
                exclude.append(mount)

        mnt = os.path.join(os.path.dirname(self._output_file), ".mnt")
        for mount in order:
            if mount == '/':
                ex = ""
                for key in exclude:
                    ex += '--exclude="{}" '.format(key)
                Worker.run(shlex.split('rsync -aHWXh {} {}/ {}/'.format(ex, self._rootfs, mnt)), logger)
                Worker.run(shlex.split('ls -l {}/'.format(mnt)), logger)
            else:
                Worker.run(shlex.split('rsync -rLtWh {}/ {}/'.format(self._rootfs + mount, mnt + mount)), logger)
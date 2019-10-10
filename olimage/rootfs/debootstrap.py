import logging
import math
import os
import shlex
import shutil

from dependency_injector import containers, providers

import olimage.environment as env

from olimage.board import Board
from olimage.container import IocContainer

from olimage.utils import Printer, RootFSStamper, Worker, Templater
from .utils.mount import Mounter

logger = logging.getLogger(__name__)


class Debootstrap(object):
    def __init__(self, **kwargs):

        self._distribution = None
        self._release = None

        self._cleanup = []

        self._board = Board(kwargs['target'])

        # Initialize dependencies
        self._partitions = kwargs['partitions']
        self._distributions = kwargs['distributions']
        self._images = kwargs['images']
        self._users = kwargs['users']

        # Check if release is valid
        release = kwargs['release']
        for dist in self._distributions:
            if release == dist:
                self._distribution = dist
                self._release = dist.recommended
            if release in dist.releases:
                self._distribution = dist
                self._release = release

        if self._release is None:
            raise Exception("Target distribution \'{}\' not found in configuration files".format(release))

        # Parse image configuration
        self._variant = kwargs['variant']

        # Set build path
        self._rootfs = os.path.join(
            env.options['workdir'], 'rootfs', "{}-{}".format(self._board.arch, self._release))
        env.paths['rootfs'] = self._rootfs

        # Configure stamper
        self._stamper = RootFSStamper(os.path.join(env.options['workdir'], 'rootfs'))

        # Output image
        self._image = os.path.join(env.paths['workdir'], 'images', 'test2.img')
        env.paths['image'] = self._image

    def __del__(self):
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
                ",".join(self._images.get_packages(self._variant)),
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
        Worker.run(shlex.split("rsync -aHWXhv {}/ {}/".format(env.paths['overlay'], self._rootfs), logger))

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

            # force_change is not mandatory
            try:
                force = user.force_change
            except AttributeError:
                force is None

            # Assuming root user is always present
            if user != "root":
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

            if force:
                Worker.chroot(
                    shlex.split("/bin/bash -c 'chage -d 0 {}'".format(user)),
                    self._rootfs,
                    logger)

    @Mounter.mount()
    @Printer("Configuring")
    def configure(self):

        # Run configure steps
        self._stamper.remove('configured')
        self._install_overlay()
        self._set_fstab()
        self._set_hostname(self._board)

        if 'configured' in self._stamper.stamps:
            return self

        # if 'users' in self._images:
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

        # Get size and add 100MiB size
        size = math.ceil(self.get_size(self._rootfs)/1024/1024) + 200

        logger.info("Creating empty file: {} with size {}".format(self._image, size))

        Worker.run(
            shlex.split("qemu-img create -f raw {} {}M".format(self._image, size)),
            logger
        )

        return self

    @Mounter.map()
    @Printer("Formatting partitions")
    def format(self):

        # Create partitions
        for part in self._partitions:
            logger.info("Formatting partition: {}".format(part))

            # Get parted related information
            device = part.device
            fstab = part.fstab

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

            part.fstab = fstab
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
            shlex.split('parted -s {} mklabel msdos'.format(self._image)),
            logger
        )

        # Create partitions
        for part in self._partitions:
            logger.info("Creating partition: {}".format(part))
            Worker.run(
                shlex.split('parted -s {} mkpart primary {} {} {}'.format(
                    self._image,
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

        mnt = os.path.join(os.path.dirname(self._image), ".mnt")
        for mount in order:
            if mount == '/':
                ex = ""
                for key in exclude:
                    ex += '--exclude="{}" '.format(key)
                Worker.run(shlex.split('rsync -aHWXh {} {}/ {}/'.format(ex, self._rootfs, mnt)), logger)
            else:
                Worker.run(shlex.split('rsync -rLtWh {}/ {}/'.format(self._rootfs + mount, mnt + mount)), logger)


class Builder(containers.DeclarativeContainer):
    debootstrap = providers.Factory(
        Debootstrap,
        distributions = IocContainer.distributions,
        partitions = IocContainer.partitions,
        images = IocContainer.images,
        users = IocContainer.users
    )
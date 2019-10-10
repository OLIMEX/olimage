# Copyright (c) 2019 Olimex Ltd.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging
import math
import os
import shlex
import shutil

import yaml

from dependency_injector import containers, providers

import olimage.environment as env

from olimage.board import Board
from olimage.container import IocContainer

from olimage.utils import Printer, RootFSStamper, Worker, Templater
from .mounter import Mounter

logger = logging.getLogger(__name__)


class Debootstrap(object):
    def __init__(self, **kwargs):

        self._distribution = None
        self._release = None

        self._cleanup = []

        self._board = Board(kwargs['target'])

        self._partitions = kwargs['partitions']
        self._distributions = kwargs['distributions']

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
        cfg = os.path.join(env.paths['configs'], 'images.yaml')
        with open(cfg, 'r') as f:
            self._images = yaml.full_load(f.read())

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

    @property
    def packages(self):
        """
        Get needed packages for debootstrap

        :return: list
        """

        def unpack(l):
            r = []
            for item in l:
                if type(item) != list:
                    r.append(item)
                    continue
                else:
                    r += unpack(item)

            return r

        return unpack(self._images['packages'][self._variant])

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
                ",".join(self.packages),
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

        for user, value in self._images['users'].items():
            passwd = value['password']

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

            if "force_change" in value and value["force_change"] is True:
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

        if 'users' in self._images:
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
        partitions=IocContainer.partitions,
        distributions=IocContainer.distributions)
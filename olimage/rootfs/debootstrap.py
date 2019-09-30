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
import re
import shlex
import shutil

import yaml

import olimage.environment as environment
from olimage.utils.printer import Printer
from olimage.utils.stamper import RootFSStamper
from olimage.utils.worker import Worker
from olimage.utils.templater import Templater

from olimage.rootfs.mount import Mount

logger = logging.getLogger(__name__)


class Release(object):
    def __init__(self, parent, name, config):
        self._parent = parent
        self._name = name
        self._config = config

    def __str__(self):
        return self._name

    @property
    def parent(self):
        return self._parent


class Distribution(object):
    def __init__(self, name, config):
        self._name = name
        self._config = config
        self._releases = {}

        for key, value in self._config['releases'].items():
            self._releases[key] = Release(self, key, value)

    def __str__(self):
        """
        Get distribution name
        :return: string
        """
        return self._name

    @property
    def components(self):
        """
        Get distribution components, e.g. main, universe, contrib, etc.

        :return: list[] with components
        """
        return self._config['components']

    @property
    def repository(self):
        """
        Get preferred repository URL

        :return: string
        """
        return self._config['repository']

    @property
    def releases(self):
        """
        Return available releases

        :return: dictionary holding releases
        """
        return self._releases


class Debootstrap(object):
    def __init__(self, board, target):
        self._target = {
            'distribution' : None,
            'release' :  None
        }
        self._targets = dict()
        self._board = board
        self._cleanup = []

        # Parse configuration file
        cfg = os.path.join(environment.paths['configs'], 'distributions.yaml')
        with open(cfg, 'r') as f:
            self._config = yaml.full_load(f.read())

        # Generate distributions objects
        for key, value in self._config.items():
            if key not in ['ubuntu', 'debian']:
                continue
            self._targets[key] = Distribution(key, value)

        # Check if target is distribution
        if target in self._targets:
            self._target['distribution'] = self._targets[target]
            self._target['release'] = self._targets[target].releases[self._config[target]['recommended']]
        else:
            for _, value in self._targets.items():
                if target in value.releases:
                    self._target['distribution'] = value
                    self._target['release'] = value.releases[target]
                    break

        for _, value in self._target.items():
            if value is None:
                raise Exception("Target distribution \'{}\' not found in configuration files".format(target))

        # Parse image configuration
        cfg = os.path.join(environment.paths['configs'], 'images.yaml')
        with open(cfg, 'r') as f:
            self._images = yaml.full_load(f.read())

        # Set build path
        self._rootfs = os.path.join(
            environment.options['workdir'], 'rootfs', "{}-{}".format(self._board.arch, self._target['release']))
        environment.paths['rootfs'] = self._rootfs

        # Configure stamper
        self._stamper = RootFSStamper(os.path.join(environment.options['workdir'], 'rootfs'))

        # Output image
        self._image = os.path.join(environment.paths['workdir'], 'images', 'test.img')
        environment.paths['image'] = self._image
        self._order = []

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
            shlex.split("qemu-debootstrap --arch={} --components={} {} {} {}".format(
                self._board.arch,
                ",".join(self._target['distribution'].components),
                self._target['release'],
                self._rootfs, self._target['distribution'].repository)),
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
        Worker.run(shlex.split("rsync -aHWXhv {}/ {}/".format(environment.paths['overlay'], self._rootfs), logger))

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

        for key, value in self._images['partitions'].items():
            logger.debug("Adding {} as UUID={} to {}".format(key, value['fstab']['uuid'], value['fstab']['mount']))

        Templater.install(
            [
                os.path.join(self._rootfs, 'etc/fstab')
            ],
            partitions = [
                {
                    'uuid' : '{:41}'.format('UUID=' + p['fstab']['uuid']),
                    'mount' : '{:15}'.format(p['fstab']['mount']),
                    'type' : '{:7}'.format(p['type']),
                    'options' : '{:8}'.format(p['fstab']['options']),
                    'dump' : '{:7}'.format(p['fstab']['dump']),
                    'pass' : '{:8}'.format(p['fstab']['pass'])
                } for _, p in self._images['partitions'].items()
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

    @Mount()
    @Printer("Configuring")
    def configure(self):

        # /etc/fstab should be always regenerated
        self._set_fstab()

        if 'configured' in self._stamper.stamps:
            return self

        # Run configure steps
        self._stamper.remove('configured')
        self._install_overlay()
        self._set_hostname(self._board)

        if 'users' in self._images:
            self._set_users()
        self._stamper.stamp('configured')

        return self

    def build(self):
        print("\nBuilding: \033[1m{}\033[0m based distribution".format(self._target['release']))

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

    @Mount(map_only=True)
    @Printer("Formatting partitions")
    def format(self):

        # Create partitions
        for key, value in self._images['partitions'].items():
            logger.info("Formatting partition: {}".format(key))

            opts = ''
            if value['type'] == 'ext4':
                opts = '-O ^64bit,^metadata_csum'

            # Make filesystem
            Worker.run(shlex.split('mkfs.{} {} {}'.format(value['type'], opts, value['device'])), logger)
            Worker.run(shlex.split('udevadm trigger {}'.format(value['device'])), logger)
            Worker.run(shlex.split('udevadm settle'.format(value['device'])), logger)

            # Generate UUID
            value['fstab']['uuid'] = Worker.run(
                shlex.split('blkid -s UUID -o value {}'.format(value['device'])),
                logger
            ).decode().splitlines()[0]

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
        for key, value in self._images['partitions'].items():
            logger.info("Creating partition: {}".format(key))
            Worker.run(
                shlex.split('parted -s {} mkpart primary {} {} {}'.format(
                    self._image,
                    'fat32' if value['type'] == 'vfat' else value['type'],
                    value['offset'],
                    '100%' if value['size'] is None else value['size']
                )),
                logger
            )

        return self

    @Mount()
    @Printer("Copying to raw image")
    def copy(self):
        exclude = ['/dev/*', '/proc/*', '/run/*', '/tmp/*', '/sys/*']
        order = []

        for key, value in self._images['partitions'].items():
            mount = value['fstab']['mount']
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


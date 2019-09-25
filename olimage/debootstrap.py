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
        self._path = os.path.join(
            environment.options['workdir'], 'rootfs', "{}-{}".format(self._board.arch, self._target['release']))

        # Configure stamper
        self._stamper = RootFSStamper(os.path.join(environment.options['workdir'], 'rootfs'))

        # Output image
        self._image = os.path.join(environment.paths['workdir'], 'images', 'test.img')
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

        if 'debootstrap' in self._stamper.stamps and os.path.exists(self._path):
            return self

        self._stamper.remove('debootstrap')
        if os.path.exists(self._path):
            shutil.rmtree(self._path)
        os.mkdir(self._path)

        Worker.run(
            shlex.split("qemu-debootstrap --arch={} --components={} {} {} {}".format(
                self._board.arch,
                ",".join(self._target['distribution'].components),
                self._target['release'],
                self._path, self._target['distribution'].repository)),
            logger
        )
        self._stamper.stamp('debootstrap')

        return self

    @Printer("Installing overlay files")
    def _install_overlay(self):
        """
        Copying overlay directory to target

        :return: self
        """
        Worker.run(shlex.split("rsync -aHWXhv {}/ {}/".format(environment.paths['overlay'], self._path), logger))

        return self

    @Printer("Setting-up system hostname")
    def _set_hostname(self, hostname):
        """
        Prepare /etc/hostname and /ets/hosts

        :param hostname: board hostname
        :return: self
        """

        Templater.install(
            [
                os.path.join(self._path, f) for f in ['etc/hostname', 'etc/hosts']
            ],
            hostname=hostname
        )

        return self

    @Printer("Configuring fstab")
    def _set_fstab(self):
        """
        Prepare /etc/fstab

        :return: self
        """

        Templater.install(
            [
                os.path.join(self._path, 'etc/fstab')
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

    @Printer("Setting-up users")
    def _set_users(self):

        for user, cfg in self._images['users'].items():
            # Assuming root user is always present
            if user != "root":
                passwd = cfg['password']
                Worker.chroot(
                    shlex.split("/bin/bash -c '(echo {}; echo {};) | adduser --gecos {} {}'".format(passwd, passwd, user, user)),
                    self._path,
                    logger
                )

    def configure(self):

        self._mount()
        self._umount()
        return

        if 'configured' in self._stamper.stamps:
            return self

        # Run configure steps
        self._stamper.remove('configured')
        self._install_overlay()
        self._set_hostname(self._board.hostname)
        self._set_fstab()

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
        size = math.ceil(self.get_size(self._path)/1024/1024) + 100

        logger.info("Creating empty file: {} with size {}".format(self._image, size))

        Worker.run(
            shlex.split("qemu-img create -f raw {} {}M".format(self._image, size)),
            logger
        )

        return self

    def _umap(self):
        """
        Umap partitions

        :return: self
        """
        self._order = []
        Worker.run(shlex.split('kpartx -dvs {}'.format(self._image)), logger)

        return self

    def _map(self):
        """
        Map partitions

        :return: self
        """

        # Map partitions
        output = Worker.run(shlex.split('kpartx -avs {}'.format(self._image)), logger).decode('utf-8', 'ignore')

        self._order = []
        for line in output.splitlines():
            w = line.split()
            if w[0] == 'add':
                device = os.path.join('/dev/mapper', w[2])
                index = int(re.match(r'^loop\d+p(\d+)$', w[2])[1])
                part, cfg = list(self._images['partitions'].items())[index - 1]

                if cfg['fstab']['mount'] == '/':
                    self._order.insert(0, (device, part, cfg))
                else:
                    self._order.append((device, part, cfg))

        return self

    def _mount(self):

        # Make sure image is mapped
        self._map()

        mount = os.path.join(os.path.dirname(self._image), ".mnt")

        if os.path.exists(mount):
            shutil.rmtree(mount)
        os.mkdir(mount)

        for device, name, cfg in self._order:
            submount = os.path.join(mount, cfg['fstab']['mount'].lstrip('/'))

            if not os.path.exists(submount):
                os.mkdir(submount)

            Worker.run(shlex.split('mount {} {}'.format(device, submount)), logger)

        Worker.run(shlex.split('df'))

        for device, _, _ in reversed(self._order):
            Worker.run(shlex.split('umount {}'.format(device)), logger)



        #
        # # Mount root
        # logger.info("Creating mounting point: {}".format(mount))
        # os.mkdir(mount)
        #
        # cfg = self._images['partitions'][part]
        # Worker.run(shlex.split('mount {} {}'.format(cfg['device'], mount)), logger)

        # self._cleanup.append(lambda: Worker.run(shlex.split('umount {}'.format(self._images['partitions'][part]['mount'])), logger))


        return self

        pass

    def _umount(self):
        self._umap()
        pass

    @Printer("Formating partitions")
    def format(self):
        # Mount device
        self._map()

        for device, name, cfg in self._order:
            opts = ''

            if cfg['type'] == 'ext4':
                opts = '-O ^64bit,^metadata_csum'

            # Make filesystem
            Worker.run(shlex.split('mkfs.{} {} {}'.format(cfg['type'], opts, device)), logger)
            Worker.run(shlex.split('udevadm trigger {}'.format(device)), logger)
            Worker.run(shlex.split('udevadm settle'.format(device)), logger)

            # Generate UUID
            cfg['fstab']['uuid'] = Worker.run(
                shlex.split('blkid -s UUID -o value {}'.format(device)),
                logger
            ).decode().splitlines()[0]

        # Umount device
        self._umap()

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

    @Printer("Copying rootfs files to the image file")
    def copy(self):
        # Copy root
        Worker.run(shlex.split('rsync -aHWXhv --exclude="/boot/*" --exclude="/dev/*" --exclude="/proc/*" --exclude="/run/*" --exclude="/tmp/*" \
                        --exclude="/sys/*" {}/ {}/'.format(self._path, self._images['partitions']['rootfs']['mount'])))

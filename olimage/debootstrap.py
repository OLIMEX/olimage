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
import os
import shlex
import shutil

import yaml

import olimage.environment as environment
from olimage.utils.printer import Printer
from olimage.utils.stamper import RootFSStamper
from olimage.utils.worker import Worker

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

        # Set build path
        self._path = os.path.join(
            environment.options['workdir'], 'rootfs', "{}-{}".format(self._board.arch, self._target['release']))

        # Configure stamper
        self._stamper = RootFSStamper(os.path.join(environment.options['workdir'], 'rootfs'))

    @Printer("Creating base system")
    def _qemu_debootstrap(self):
        """
        Create bare minimum rootfs

        :return: None
        """

        if 'debootstrap' in self._stamper.stamps and os.path.exists(self._path):
            return

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

    # @Printer("Setting-up system hostname")
    def _set_hostname(self, hostname):

        # Write hostname ot /etc/hostname
        path = os.path.join(self._path, 'etc/hostname')
        with open(path, 'w') as f:
            f.write("{}\n".format(hostname))

        # Add hostname to /etc/hosts
        path = os.path.join(self._path, 'etc/hosts')
        with open(path, 'r') as f:
            content = f.readlines()

        with open(path, 'w') as f:
            f.write("127.0.1.1\t{}\n".format(hostname))
            for line in content:
                if hostname not in line:
                    f.write('{}'.format(line))

    def build(self):
        print("\nBuilding: \033[1m{}\033[0m based distribution".format(self._target['release']))

        self._qemu_debootstrap()
        # self._set_hostname('a64-olinuxino')
        return




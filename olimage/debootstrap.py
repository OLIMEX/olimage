import logging
import os
import subprocess
import shlex
import logging
import yaml

import environment

import shutil

from utils.worker import Worker
from utils.printer import Printer
from utils.stamper import RootFSStamper

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
    def __init__(self, arch, target):
        self._target = dict()
        self._targets = dict()
        self._arch = arch

        # Parse configuration file
        cfg = os.path.dirname(os.path.abspath(__file__))
        cfg = os.path.join(cfg, 'configs/distributions.yaml')
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
            self._target['release'] = self._targets[target].releases[self._config[target]['recomended']]
        else:
            for _, value in self._targets.items():
                if target in value.releases:
                    self._target['distribution'] = value
                    self._target['release'] = value.releases[target]
                    break

        for _, value in self._target.items():
            if value is None:
                raise Exception("Not font")  # TODO: Fix this

        # Set build path
        self._path = os.path.join(environment.env['workdir'], 'rootfs', "{}-{}".format(self._arch, self._target['release']))

        # Configure stamper
        self._stamper = RootFSStamper(os.path.join(environment.env['workdir'], 'rootfs'))

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
                self._arch,
                ",".join(self._target['distribution'].components),
                self._target['release'],
                self._path, self._target['distribution'].repository)),
            logger
        )
        self._stamper.stamp('debootstrap')

    @Printer("Setting-up system hostname")
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
        self._set_hostname('a64-olinuxino')
        return




import olimage.environment as env

from olimage.core.io import Console
from olimage.core.parsers import (NetworkParser, Interface)
from olimage.core.utils import Utils

from .base import SetupAbstract


class SetupNetwork(SetupAbstract):

    def setup(self):

        for interface in NetworkParser().interfaces:
            interface: Interface

            with Console('Installing: \'/etc/network/interfaces\''):
                Utils.install('/etc/network/interfaces')

            with Console("Configuring interface: \'{}\'".format(str(interface))):
                file = '/etc/network/interfaces.d/{}'.format(str(interface))

                source = env.paths['overlay'] + '/etc/network/interfaces.d/default'
                destination = env.paths['build'] + file

                # Install source list
                Utils.shell.run("install -m 644 {} {}".format(source, destination))
                Utils.template.install(destination, interface=interface)

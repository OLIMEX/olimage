import olimage.environment as env

from olimage.core.io import Console
from olimage.core.utils import Utils

from .base import SetupAbstract


class SetupKernel(SetupAbstract):
    def setup(self):

        with Console("Installing Linux image"):
            Utils.shell.chroot('apt-get install -y {}'.format(' '.join(self.packages)))

        with Console("Configuring modules"):
            with open(env.paths['build'] + '/etc/modules', 'a') as f:
                for module in self.parser.modules['enable']:
                    f.write(module + '\n')

                # Append new line at the end of file
                f.write('\n')

            with open(env.paths['build'] + '/etc/modprobe.d/blacklist-olinuxino.conf', 'w') as f:
                for module in self.parser.modules['blacklist']:
                    f.write("blacklist {}\n".format(module))

                # Append new line at the end of file
                f.write('\n')

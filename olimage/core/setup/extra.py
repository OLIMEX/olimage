import olimage.environment as env

from olimage.core.io import Console
from olimage.core.utils import Utils

from .base import SetupAbstract


class SetupExtra(SetupAbstract):

    def setup(self):
        Utils.install('/etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml')
        Utils.install('/etc/modprobe.d/rtl8192cu.conf')
        Utils.install('/etc/modprobe.d/rtl8723bs.conf')
        Utils.shell.run('sed -i "s/^#DefaultTimeoutStopSec.*/DefaultTimeoutStopSec=15s/g" {}/etc/systemd/system.conf'.format(env.paths['build']))
        Utils.shell.run('sed -i "s/^#Storage=.*/Storage=volatile/g" {}/etc/systemd/journald.conf'.format(env.paths['build']))
        Utils.shell.run('sed -i "s/^#SystemMaxUse=.*/SystemMaxUse=64M/g" {}/etc/systemd/journald.conf'.format(env.paths['build']))
        Utils.shell.run('sed -i "s/^#RuntimeMaxFileSize=.*/RuntimeMaxFileSize=8M/g" {}/etc/systemd/journald.conf'.format(env.paths['build']))
        Utils.shell.run('sed -i "s/^#RuntimeMaxUse=.*/RuntimeMaxUse=16M/g" {}/etc/systemd/journald.conf'.format(env.paths['build']))

        for file in env.options['extra_file']:
            with Console(f'Extra file: {file}'):
                Utils.install(file)
        for cmd in env.options['extra_cmd']:
            with Console(f'Extra command: {cmd}'):
                Utils.shell.chroot(cmd)
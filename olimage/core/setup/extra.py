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
        Utils.shell.run('sed -i "s/^#SystemMaxUse=.*/SystemMaxUse=32M/g" {}/etc/systemd/journald.conf'.format(env.paths['build']))
        Utils.shell.run('sed -i "s/^#SystemMaxFileSize=.*/SystemMaxFileSize=16M/g" {}/etc/systemd/journald.conf'.format(env.paths['build']))
        Utils.shell.run('sed -i "s/^#SystemKeepFree=.*/SystemKeepFree=64M/g" {}/etc/systemd/journald.conf'.format(env.paths['build']))
        Utils.shell.run('sed -i "s/^#RuntimeMaxUse=.*/RuntimeMaxUse=32M/g" {}/etc/systemd/journald.conf'.format(env.paths['build']))
        Utils.shell.run('sed -i "s/^#RuntimeMaxFileSize=.*/RuntimeMaxFileSize=16M/g" {}/etc/systemd/journald.conf'.format(env.paths['build']))
        Utils.shell.run('sed -i "s/^#RuntimeKeepFree=.*/RuntimeKeepFree=64M/g" {}/etc/systemd/journald.conf'.format(env.paths['build']))

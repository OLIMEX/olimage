import olimage.environment as env

from olimage.core.io import Console
from olimage.core.utils import Utils

from .base import SetupAbstract


class SetupExtra(SetupAbstract):

    def setup(self):
        Utils.install('/etc/modprobe.d/rtl8192cu.conf')
        Utils.install('/etc/modprobe.d/rtl8723bs.conf')

        Utils.install('/etc/resolv.conf')

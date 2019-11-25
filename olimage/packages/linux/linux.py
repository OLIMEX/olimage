import logging
import os

from olimage.core.stamp import stamp
from olimage.core.utils import Utils
from olimage.packages.package import AbstractPackage


logger = logging.getLogger(__name__)


class Linux(AbstractPackage):

    def __init__(self, boards):

        self._name = 'linux'

        super().__init__(boards)

        # Some global data
        self._arch = self._board.arch
        self._toolchain = self._package.toolchain.prefix

    @staticmethod
    def alias() -> str:
        return 'linux'

    @property
    def deb(self) -> str:
        return 'linux-image-{version}_{version}_arm64.deb'.format(version=self._package.version)

    def _merge_fragments(self):
        path = self.paths['compile']
        script = os.path.join(path, 'scripts/kconfig/merge_config.sh')
        config = os.path.join(path, '.config')

        logger.info("Merging fragment files")
        for root, _, fragments in os.walk(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fragments')):
            for fragment in fragments:
                # Merge only .fragment files
                if not fragment.endswith('.fragment'):
                    continue

                # First merge config files
                logger.debug("Merging fragment file: {}".format(fragment))
                Utils.shell.run(
                    "/bin/bash -c '{} -m -O {} {} {}'".format(script, path, config, os.path.join(root, fragment)))

                # Second, regenerate config file
                Utils.shell.run("make -C {} ARCH={} oldconfig".format(self.paths['compile'], self._arch))

    @stamp
    def configure(self):
        """
        Configure sources using defconfig

        :return: None
        """

        # Select defconfig
        if self._package.defconfig is not None:
            defconfig = self._package.defconfig + '_defconfig'
        else:
            defconfig = 'defconfig'

        # Make defconfig
        Utils.shell.run("make -C {} ARCH={} {}".format(
            self.paths['compile'],
            self._arch,
            defconfig))

        # Merge fragments
        self._merge_fragments()

    @stamp
    def build(self):
        Utils.shell.run("make -C {} ARCH={} CROSS_COMPILE={} -j {}".format(
            self.paths['compile'],
            self._arch,
            self._toolchain,
            1 if os.cpu_count() is None else os.cpu_count(),
            ' '.join(self._package.targets))
        )

    @stamp
    def package(self):
        """
        Package linux kernel

        :return: None
        """
        Utils.shell.run("make -C {} KDEB_PKGVERSION={} LOCALVERSION={} ARCH={} CROSS_COMPILE={} bindeb-pkg".format(
            self.paths['compile'],
            self._package.version,
            self._package.localversion,
            self._arch,
            self._toolchain)
        )

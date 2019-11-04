import logging
import os

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
        self._pkg_version = None

    @staticmethod
    def alias() -> str:
        return 'linux'

    @property
    def deb(self) -> str:
        return self._output_package

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
                self._builder.make("ARCH={} oldconfig".format(self._arch))

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
        self._builder.make("ARCH={} {}".format(self._arch, defconfig))

        # Merge fragments
        self._merge_fragments()

    def build(self):
        self._builder.make("ARCH={} CROSS_COMPILE={} {}".format(self._arch,self._toolchain,' '.join(self._package.targets)))

    def package(self):
        """
        Package linux kernel

        :return: None
        """
        self._pkg_version = self._builder.make("kernelversion").decode().splitlines()[1] + self._package.version
        self._builder.make("KDEB_PKGVERSION={} LOCALVERSION={} ARCH={} CROSS_COMPILE={} bindeb-pkg".format(self._pkg_version, self._package.version, self._arch, self._toolchain))

        self._output_package = 'linux-image-{}_{}_arm64.deb'.format(self._pkg_version, self._pkg_version)

from olimage.core.utils import Utils
from olimage.packages.package import AbstractPackage


class OlimexSunxiOverlays(AbstractPackage):
    def __init__(self, boards):

        self._name = 'olimex-sunxi-overlays'
        super().__init__(boards)

    @staticmethod
    def alias():
        """
        Get modules alias

        :return: string alias
        """
        return 'olimex-sunxi-overlays'

    @property
    def deb(self) -> str:
        return "olimex-sunxi-overlays_1.0.0_all.deb"

    def package(self):
        """
        Generate .deb file

        :return: None
        """

        # Build package
        # This command returns error since target and host arch doesn't match. We are using only the generated .deb
        # file, so ignore the error for now.
        Utils.shell.run(
            'cd {} && debuild -us -uc'.format(self._builder.paths['extract']),
            shell=True,
            ignore_fail=True,
            log_error=False
        )

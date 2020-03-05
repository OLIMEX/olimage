from olimage.core.parsers.exceptions import ParserException


class BoardLoading(object):
    """
    Parse loading addresses.

    Those are used by boot.cmd, loaded by the
    U-Boot blob.
    """
    def __init__(self, data) -> None:
        self._data = data

    @property
    def data(self) -> dict:
        """
        Get the unparsed data

        :return:
        """
        return self._data

    @property
    def fdt(self) -> str:
        """
        Get FDT load address

        :return: fdt loading address as string
        """
        if 'fdt' in self._data:
            return self._data['fdt']

        raise ParserException("\'fdt\' not defined!")

    @property
    def fit(self) -> str:
        """
        Get FIT load address

        :return: fit loading address as string
        """
        if 'fit' in self._data:
            return self._data['fit']

        raise ParserException("\'fit\' not defined!")

    @property
    def kernel(self) -> str:
        """
        Get kernel load address

        :return: kernel loading address as string
        """
        if 'kernel' in self._data:
            return self._data['kernel']

        raise ParserException("\'kernel\' not defined!")

    @property
    def overlays(self) -> str:
        """
        Get overlays load address

        :return: overlays loading address as string
        """
        if 'overlays' in self._data:
            return self._data['overlays']

        raise ParserException("\'overlays\' not defined!")

    @property
    def ramdisk(self) -> str:
        """
        Get ramdisk load address

        :return: ramdisk loading address as string
        """
        if 'ramdisk' in self._data:
            return self._data['ramdisk']

        raise ParserException("\'ramdisk\' not defined!")

    @property
    def uenv(self) -> str:
        """
        Get uEnv.txt load address

        :return: uenv loading address as string
        """
        if 'uenv' in self._data:
            return self._data['uenv']

        raise ParserException("\'uenv\' not defined!")

class BoardLoading(object):
    """
    Parse loading addresses
    """
    def __init__(self, data) -> None:
        self._data = data

    @property
    def data(self) -> dict:
        return self._data

    @property
    def fdt(self) -> str:
        return self._data['fdt']

    @property
    def fit(self) -> str:
        return self._data['fit']

    @property
    def kernel(self) -> str:
        return self._data['kernel']

    @property
    def overlays(self) -> str:
        return self._data['overlays']

    @property
    def ramdisk(self) -> str:
        return self._data['ramdisk']

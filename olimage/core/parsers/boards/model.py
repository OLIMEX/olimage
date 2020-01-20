class Model(object):
    """
    Parse single board model
    """
    def __init__(self, name, data) -> None:
        self._name = name
        self._data = data

    def __str__(self) -> str:
        return self._name

    @property
    def id(self) -> int:
        """
        Get model's ID number

        :return: model id
        """
        return int(self._data['id'])

    @property
    def fdt(self) -> str:
        """
        Get model's default FDT blob

        :return: FTD filename
        """
        return self._data['fdt']

    @property
    def overlays(self) -> list:
        """
        Get model's default overlays

        :return: FDTO filenames list
        """
        overlays = self._data['overlays']
        if overlays is None:
            return []
        else:
            return overlays

class PackagesBase(object):
    def __init__(self, name: str, data: dict) -> None:
        self._name = name
        self._data = data

    def __str__(self) -> str:
        return self._name

    @property
    def packages(self) -> list:
        """
        Get flattened list with packages

        :return: packages list
        """
        def flat(data):
            _data = []
            for p in data:
                if isinstance(p, list):
                    _data += flat(p)
                elif isinstance(p, str):
                    _data.append(p)
                else:
                    raise Exception("Unsupported type: \'{}\'".format(type(p)))
            return _data

        return flat(self._data['packages'])

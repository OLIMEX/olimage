from .parser import GenericLoader


class Variant(object):
    def __init__(self, name: str, data: dict) -> None:
        self._name = name
        self._data = data

    def __str__(self) -> str:
        return self._name

    @property
    def packages(self) -> list:

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


class Variants(GenericLoader):
    def __init__(self) -> None:
        super().__init__("variants", Variant, prefix='core')

    def get_variant(self, name: str) -> Variant:
        for variant in self._objects:
            if name.lower() == str(variant).lower():
                return variant

        raise Exception("Variant not found: \"{}\"".format(name))

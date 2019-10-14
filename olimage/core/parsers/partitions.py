from .parser import GenericLoader


class FSTab(object):
    def __init__(self, data: dict) -> None:
        self._data = data
        self._uuid = None

    @property
    def type(self) -> str:
        return self._data['type']

    @property
    def mount(self) -> str:
        return self._data['mount']

    @property
    def options(self) -> str:
        return self._data['options']

    @property
    def dump(self) -> int:
        return int(self._data['dump'])

    @property
    def passno(self) -> int:
        return int(self._data['passno'])

    @property
    def uuid(self) -> str:
        return self._uuid

    @uuid.setter
    def uuid(self, value: str):
        self._uuid = value


class Parted(object):
    def __init__(self, data: dict) -> None:
        self._data = data

    @property
    def type(self) -> str:
        return self._data['type']

    @property
    def start(self) -> str:
        return self._data['start']

    @property
    def end(self) -> str:
        return self._data['end']


class Partition(object):
    def __init__(self, name: str, data: dict) -> None:
        self._name = name
        self._data = data

        self._device = None

        self._fstab = FSTab(self._data['fstab'])
        self._parted = Parted(self._data['parted'])

    def __str__(self):
        return self._name

    @property
    def fstab(self) -> object:
        return self._fstab

    @property
    def parted(self) -> object:
        return self._parted

    @property
    def device(self) -> str:
        return self._device

    @device.setter
    def device(self, name: str):
        self._device = name


class Partitions(GenericLoader):
    def __init__(self) -> None:
        super().__init__("partitions", Partition)


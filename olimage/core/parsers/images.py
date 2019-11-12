from .parser import GenericLoader


class Image(object):
    def __init__(self, name: str, data: dict) -> None:
        self._name = name
        self._data = data

    def __str__(self) -> str:
        return self._name

    @property
    def packages(self) -> list:
        return self._data['packages']


class Images(GenericLoader):
    def __init__(self) -> None:
        super().__init__("images", Image)

    def get_image(self, name: str) -> Image:
        for image in self._objects:
            if name.lower() == str(image).lower():
                return image

        raise Exception("Rootfs variant not found: \"{}\"".format(name))
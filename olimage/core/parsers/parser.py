import abc
import os

import yaml

import olimage.environment as env


class LoaderBase(metaclass=abc.ABCMeta):

    def __init__(self):
        self._objects = []
        self._loaded = False

    def __iter__(self):
        self._load()
        self._iter = iter(self._objects)
        return self

    def __next__(self):
        return next(self._iter)

    def __getitem__(self, item):
        self._load()
        return self._objects[item]

    def _load(self):
        if self._loaded:
            return

        self.load()

        self._loaded = True

    @abc.abstractmethod
    def load(self):
        pass


class GenericLoader(LoaderBase):
    config = None

    def load(self):
        if self.config is None:
            return

        # Read configuration file
        with open(os.path.join(env.paths['configs'], '{}.yaml'.format(self.config))) as f:
            data = yaml.full_load(f.read())[self.config]

        # Generate objects
        for key, value in data.items():
            self._objects.append(Parser(key, value))


class Parser(object):
    """
    Generic class for configuration mapping
    """
    def __init__(self, name: str, data: dict):
        """
        Initialize generic config object

        :param name: config name
        :param data: config data
        """
        self._name = name
        self._data = data

    def __str__(self):
        return self._name

    def __getattr__(self, item):
        # Check if item is in the config dict
        if item not in self._data:
            raise AttributeError("\'{}\' object has no attribute \'{}\'".format(self.__class__.__name__, item))

        # If data[item] is dictionary create new ORM object
        if isinstance(self._data[item], dict):
            return Parser(item, self._data[item])

        # Return value
        return self._data[item]

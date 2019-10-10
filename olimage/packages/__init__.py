import importlib
import inspect
import pkgutil
import os

import click


from olimage.board import Board
from olimage.utils import Printer

import olimage.environment as env


class Access(type):

    _obj = object()

    def __new__(mcs, *args, **kwargs):
        private = {key
                   for base in args[1]
                   for key, value in vars(base).items()
                   if callable(value) and mcs._is_final(value)}

        for key in args[2]:
            if key in private:
                raise RuntimeError('Class \'{}\' cannot override the \'{}\' method'.format(args[0], key))
        return super().__new__(mcs, *args, **kwargs)

    @classmethod
    def _is_final(mcs, method):
        try:
            return method._final is mcs._obj
        except AttributeError:
            return False

    @classmethod
    def final(mcs, method):
        method._final = mcs._obj
        return method


class Package(object, metaclass=Access):

    def __init__(self, **kwargs):
        self._callbacks = kwargs

    @staticmethod
    def alias():
        """
        Return class alias
        :return:
        """
        raise NotImplementedError("'alias' method is not implemented")

    @property
    def dependency(self):
        """
        Get package dependency
        :return: list of dependency
        """
        raise NotImplementedError("'dependency' method not implemented")

    @Printer("Downloading")
    @Access.final
    def download(self):
        if 'download' in self._callbacks:
            self._callbacks['download']()
        return self

    @Printer("Configuring")
    @Access.final
    def configure(self):
        if 'configure' in self._callbacks:
            self._callbacks['configure']()
        return self

    @Printer("Building")
    @Access.final
    def build(self):
        if 'build' in self._callbacks:
            self._callbacks['build']()
        return self

    @Printer("Packaging")
    @Access.final
    def package(self):
        if 'package' in self._callbacks:
            self._callbacks['package']()
        return self

    @Printer("Installing")
    @Access.final
    def install(self):
        if 'install' in self._callbacks:
            self._callbacks['install']()
        return self


# Scan for package modules
Pool = {}
for (path, dirs, files) in os.walk(os.path.dirname(__file__)):
    for d in dirs:
        for (_, name, _) in pkgutil.walk_packages([os.path.join(path, d)]):
            # Import module
            module = importlib.import_module(__name__ + '.' + d + '.' + name)

            # Get all classes
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, Package) and cls != Package:
                    try:
                        Pool[cls.alias()] = cls
                    except NotImplementedError:
                        pass
                    except AttributeError:
                        pass


def _build_package(obj):
    obj.download()
    obj.configure()
    obj.build()
    obj.package()
    obj.install()

@click.command(name="package")
# Options
# @click.option("--step", type=click.Choice(['download', 'configure', 'build', 'package']), default='install')
# Arguments
@click.argument("target")
@click.argument("package")
def build_package(**kwargs):

    # Update env options
    env.options.update(kwargs)

    # Generate board object
    b = Board(kwargs['target'])

    # Build board packages
    board_packages = {}
    for key, value in b.packages.items():
        try:
            obj = Pool[key]
            board_packages[key] = obj(value)
        except KeyError as e:
            raise Exception("Missing package builder: {}".format(e))

    # step = kwargs['step']

    if kwargs['package'] == 'all':
        for key, value in board_packages.items():
            print("\nBuilding: \033[1m{}\033[0m".format(key))
            _build_package(value)
    else:
        _build_package(board_packages[kwargs['package']])







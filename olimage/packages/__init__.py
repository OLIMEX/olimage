import importlib
import inspect
import pkgutil
import os

from olimage.utils.printer import Printer

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


Pool = {}

# Scan for package modules
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




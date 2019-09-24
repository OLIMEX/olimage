import importlib
import inspect
import pkgutil
import sys
import os


class Package(object):

    @staticmethod
    def alias():
        raise NotImplementedError("'alias' method is not implemented")

    @property
    def dependency(self):
        raise NotImplementedError("'dependency' method not implemented")

    def build(self):
        raise NotImplementedError("'build' method not implemented")

    def package(self):
        raise NotImplementedError("'package' method not implemented")


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




import importlib
import inspect
import pkgutil
import sys


class BSP(object):

    @staticmethod
    def generate(target, *args, **kwargs):

        # Walk through all submodules
        package = sys.modules[__name__]
        for _, name, _ in pkgutil.walk_packages(package.__path__):

            # Import module
            module = importlib.import_module(__name__ + '.' + name)

            # Get all classes
            for _, cls in inspect.getmembers(module, inspect.isclass):
                try:
                    if cls.alias() == target:
                        # TODO: Check mandatory fields in the config
                        return cls(*args, **kwargs)
                except NotImplementedError:
                    pass
                except AttributeError:
                    pass
        return None

    @staticmethod
    def alias():
        raise NotImplementedError("'alias' method is not implemented")

    @property
    def dependency(self):
        raise NotImplementedError("'dependency' method not implemented")

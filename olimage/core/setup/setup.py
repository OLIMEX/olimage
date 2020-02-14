import os
import importlib
import inspect

import olimage.environment as env

from .apt import SetupApt
from .boot import SetupBoot
from .console import SetupConsole
from .fstab import SetupFstab
from .hostname import SetupHostname
from .locales import SetupLocales
from .timezone import SetupTimezone
from .user import SetupUser


class SetupMeta(type):
    def __getattribute__(self, item):

        if env.obj_graph is None:
            return type.__getattribute__(self, item)

        modules = {}
        for (path, dirs, files) in os.walk(os.path.dirname(__file__)):
            # Don't walk subdirectories
            if path != os.path.dirname(__file__):
                continue

            for file in files:
                file = str(file)
                if file.endswith('.py'):
                    module = os.path.splitext(file)[0]

                    if module == '__init__' or module == 'setup':
                        continue

                    module_path = 'olimage.core.setup.' + module
                    obj = importlib.import_module(module_path)

                    for _, cls in inspect.getmembers(obj, inspect.isclass):
                        if cls.__module__ != module_path:
                            continue

                        modules[module] = cls

        if item in modules:
            return env.obj_graph.provide(modules[item])

        return type.__getattribute__(self, item)


class Setup(object, metaclass=SetupMeta):
    apt: SetupApt
    boot: SetupBoot
    console: SetupConsole
    fstab: SetupFstab
    hostname: SetupHostname
    locales: SetupLocales
    timezone: SetupTimezone
    user: SetupUser

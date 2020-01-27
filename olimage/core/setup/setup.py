import os
import importlib
import inspect

import olimage.environment as env

from .apt import Apt
from .boot import Boot
from .console import Console
from .fstab import FSTab
from .hostname import Hostname
from .locales import Locales
from .ssh import SSH
from .timezone import Timezone
from .user import User


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
    apt: Apt
    boot: Boot
    console: Console
    fstab: FSTab
    hostname: Hostname
    locales: Locales
    ssh: SSH
    timezone: Timezone
    user: User

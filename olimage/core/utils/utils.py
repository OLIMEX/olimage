import os
import importlib
import inspect

import olimage.environment as env

from .archive import Archive
from .install import Install
from .patch import Patch
from .qemu import Qemu
from .shell import Shell
from .systemctl import Systemctl
from .template import Template
from .packagelist import Packagelist


class UtilsMeta(type):
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

                    if module == '__init__' or module == 'utils':
                        continue

                    module_path = 'olimage.core.utils.' + module
                    obj = importlib.import_module(module_path)

                    for name, cls in inspect.getmembers(obj, inspect.isclass):
                        if cls.__module__ != module_path:
                            continue

                        modules[module] = cls

        if item in modules:
            return env.obj_graph.provide(modules[item])

        return type.__getattribute__(self, item)


class Utils(object, metaclass=UtilsMeta):
    archive: Archive
    install: Install
    patch: Patch
    qemu: Qemu
    shell: Shell
    systemctl: Systemctl
    template: Template
    packagelist: Packagelist

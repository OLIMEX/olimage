import olimage.environment as env

from .archive import Archive
from .patch import Patch
from .qemu import Qemu
from .shell import Shell


class UtilsMeta(type):
    def __getattribute__(self, item):
        if item == 'archive':
            return env.obj_graph.provide(Archive)
        elif item == 'patch':
            return env.obj_graph.provide(Patch)
        elif item == 'qemu':
            return env.obj_graph.provide(Qemu)
        elif item == 'shell':
            return env.obj_graph.provide(Shell)
        else:
            return type.__getattribute__(self, item)

    def __dir__(self):
        return type.__dir__(self) + ['archive', 'patch', 'qemu', 'shell']


class Utils(object, metaclass=UtilsMeta):
    pass

import olimage.environment as env

from .archive import Archive
from .download import Download
from .patch import Patch
from .qemu import Qemu
from .shell import Shell
from .template import Template


class UtilsMeta(type):
    def __getattribute__(self, item):
        if item == 'archive':
            return env.obj_graph.provide(Archive)
        elif item == 'download':
            return env.obj_graph.provide(Download)
        elif item == 'patch':
            return env.obj_graph.provide(Patch)
        elif item == 'qemu':
            return env.obj_graph.provide(Qemu)
        elif item == 'shell':
            return env.obj_graph.provide(Shell)
        elif item == 'template':
            return env.obj_graph.provide(Template)
        else:
            return type.__getattribute__(self, item)


class Utils(object, metaclass=UtilsMeta):
    archive = None
    download = None
    patch = None
    qemu = None
    shell = None
    template = None

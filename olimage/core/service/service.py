import olimage.environment as env

from .apt_cache import AptCache
from .resize import Resize


class ServiceMeta(type):
    def __getattribute__(self, item):
        if env.obj_graph is None:
            return type.__getattribute__(self, item)

        if item == 'apt_cache':
            return env.obj_graph.provide(AptCache)
        elif item == 'resize':
            return env.obj_graph.provide(Resize)

        return type.__getattribute__(self, item)


class Service(metaclass=ServiceMeta):
    apt_cache: AptCache
    resize: Resize


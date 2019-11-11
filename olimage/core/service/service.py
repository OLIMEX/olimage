import olimage.environment as env

from .apt_cache import AptCache
from .resize import Resize


class ServiceMeta(type):
    def __getattribute__(self, item):
        if item == 'resize':
            return env.obj_graph.provide(Resize)
        if item == 'apt_cache':
            return env.obj_graph.provide(AptCache)
        else:
            return type.__getattribute__(self, item)


class Service(metaclass=ServiceMeta):
    resize = None
    apt_cache = None

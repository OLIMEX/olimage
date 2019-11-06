import olimage.environment as env
from .resize import Resize


class ServiceMeta(type):
    def __getattribute__(self, item):
        if item == 'resize':
            return env.obj_graph.provide(Resize)
        else:
            return type.__getattribute__(self, item)


class Service(metaclass=ServiceMeta):
    resize = None
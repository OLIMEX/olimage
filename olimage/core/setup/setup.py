import olimage.environment as env

from .fstab import FSTab
from .getty import Getty
from .hostname import Hostname
from .locales import Locales
from .timezone import Timezone
from .user import User


class SetupMeta(type):
    def __getattribute__(self, item):
        if item == 'fstab':
            return env.obj_graph.provide(FSTab)
        elif item == 'getty':
            return env.obj_graph.provide(Getty)
        elif item == 'hostname':
            return env.obj_graph.provide(Hostname)
        elif item == 'locales':
            return env.obj_graph.provide(Locales)
        elif item == 'timezone':
            return env.obj_graph.provide(Timezone)
        elif item == 'user':
            return env.obj_graph.provide(User)
        else:
            return type.__getattribute__(self, item)


class Setup(object, metaclass=SetupMeta):
    fstab = None
    getty = None
    hostname = None
    locales = None
    timezone = None
    user = None

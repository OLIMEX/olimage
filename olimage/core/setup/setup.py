from typing import Iterable

import olimage.environment as env

from .apt import Apt
from .console import Console
from .fstab import FSTab
from .getty import Getty
from .hostname import Hostname
from .locales import Locales
from .ssh import SSH
from .timezone import Timezone
from .user import User


class SetupMeta(type):
    def __getattribute__(self, item):

        if env.obj_graph is None:
            return type.__getattribute__(self, item)

        mapping = {
            'apt': env.obj_graph.provide(Apt),
            'console': env.obj_graph.provide(Console),
            'fstab': env.obj_graph.provide(FSTab),
            'getty': env.obj_graph.provide(Getty),
            'hostname': env.obj_graph.provide(Hostname),
            'locales': env.obj_graph.provide(Locales),
            'ssh': env.obj_graph.provide(SSH),
            'timezone': env.obj_graph.provide(Timezone),
            'user': env.obj_graph.provide(User),
        }

        if item in mapping:
            return mapping[item]

        return type.__getattribute__(self, item)


class Setup(object, metaclass=SetupMeta):
    apt: Apt
    console: Console
    fstab: FSTab
    getty: Getty
    hostname: Hostname
    locales: Locales
    ssh: SSH
    timezone: Timezone
    user: User

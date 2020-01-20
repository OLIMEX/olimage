import click

import olimage.environment as env

from .parameters import parameters
from .rootfs import Rootfs


__all__ = [
    'Rootfs'
]


@click.command(name="rootfs")
@parameters
def build_rootfs(**kwargs):

    # Update environment options
    env.options.update(kwargs)

    # Build rootfs
    rootfs: Rootfs = env.obj_graph.provide(Rootfs)

    print("\nBuilding: \033[1m{}\033[0m based distribution".format(env.options['release']))
    rootfs.build()
    rootfs.configure()
    rootfs.services()
    rootfs.cleanup()
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

    print("rootfs: Building")
    rootfs.build()

    print("rootfs: Configuring")
    rootfs.configure()
    rootfs.services()

    print("rootfs: Cleanup")
    rootfs.cleanup()
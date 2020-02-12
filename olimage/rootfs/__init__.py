import click

import olimage.environment as env

from olimage.core.io import Console

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
    console = Console()

    console.info("Creating the target file-system...")

    with Console("Building"):
        rootfs.build()

    with Console("Configuring"):
        rootfs.configure()
        rootfs.services()

    with Console("Cleanup"):
        rootfs.cleanup()
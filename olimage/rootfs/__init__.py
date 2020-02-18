import click

import olimage.environment as env

from olimage.core.io import Console

from .parameters import parameters
from .rootfs import Rootfs


@click.command(name="rootfs")
@parameters
def build_rootfs(**kwargs):

    # Update environment options
    env.options.update(kwargs)

    # Build rootfs
    root: Rootfs = env.obj_graph.provide(Rootfs)
    console = Console()

    console.info("Creating the target file-system...")

    with Console("Building"):
        root.build()

    with Console("Configuring"):
        root.configure()
        root.services()

    with Console("Cleanup"):
        root.cleanup()
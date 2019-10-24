import click

import olimage.environment as env

from .rootfs import Rootfs


@click.command(name="rootfs")
# Arguments
@click.argument("board")
@click.argument("release")
@click.argument("variant", type=click.Choice(['minimal', 'base', 'full']))
def build_rootfs(**kwargs):

    # Update environment options
    env.options.update(kwargs)

    # Build rootfs
    d: Rootfs = env.obj_graph.provide(Rootfs)
    d.build()

    # Generate empty target image
    d.generate().partition()

    # Create filesystems
    d.format()

    # Make final configurations
    d.configure()

    # Copy rootfs files to the image
    d.copy()
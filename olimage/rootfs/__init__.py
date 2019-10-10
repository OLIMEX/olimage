import click
import os

import olimage.environment as env

from .debootstrap import Debootstrap, Builder
from .mounter import Map, Mount


@click.command(name="rootfs")
# Arguments
@click.argument("target")
@click.argument("release")
@click.argument("variant", type=click.Choice(['minimal', 'base', 'full']))
# Options
@click.option("--overlay", default="rootfs/overlay", help="Path to overlay files")
def build_rootfs(**kwargs):

    # Update environment options
    env.options.update(kwargs)
    env.paths['overlay'] = os.path.join(env.paths['root'], kwargs['overlay'])

    # Build rootfs
    d = Builder.debootstrap(**kwargs)
    d.build()

    # Generate empty target image
    d.generate().partition()

    # Create filesystems
    d.format()

    # Make final configurations
    d.configure()

    # Copy rootfs files to the image
    d.copy()
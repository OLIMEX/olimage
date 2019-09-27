import click
import os

import olimage.environment as environment

from olimage.board import Board
from olimage.rootfs.debootstrap import Debootstrap


@click.command(name="rootfs")
# Arguments
@click.argument("target")
@click.argument("release")
# Options
@click.option("--overlay", default="rootfs/overlay", help="Path to overlay files")
def build_rootfs(**kwargs):

    # Update environment options
    environment.options.update(kwargs)
    environment.paths['overlay'] = os.path.join(environment.paths['root'], kwargs['overlay'])


    # Generate board object
    b = Board(kwargs['target'])

    # Build rootfs
    d = Debootstrap(b, kwargs['release'])
    d.build()

    # Generate empty target image
    d.generate().partition()

    # Create filesystems
    d.format()

    # Make final configurations
    d.configure()

    # Copy rootfs files to the image
    d.copy()

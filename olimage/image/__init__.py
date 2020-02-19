import click
import os

import olimage.environment as env
from olimage.core.io import Console

from .image import Image
from .parameters import parameters

__all__ = [
    'Image'
]


@click.command(name="image")
@parameters
@click.pass_context
def build_image(ctx: click.Context, **kwargs):

    kwargs['output'] = os.path.join(env.paths['images'], kwargs['output'])

    # Update env options
    env.options.update(kwargs)

    # Invoke build rootfs
    import olimage.rootfs
    ctx.invoke(olimage.rootfs.build_rootfs, **kwargs)

    _image: Image = env.obj_graph.provide(Image)
    console = Console()

    console.info("Creating the target file-system...")

    with Console("Generating black image"):
        _image.generate()
        _image.partition()
        _image.format()
        _image.bootloader()

    with Console("Copying target files"):
        _image.copy(env.paths['build'])

    with Console("Configuring"):
        _image.configure()



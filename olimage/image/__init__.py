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

    # Invoke build filesystem
    import olimage.filesystem
    ctx.invoke(olimage.filesystem.build_filesystem, **kwargs)

    _image: Image = env.obj_graph.provide(Image)
    console = Console()

    console.info("Creating image \'{}\'...".format(os.path.basename(kwargs['output'])))

    with Console("Generating black image"):
        _image.generate()
        _image.partition()
        _image.format()
        _image.bootloader()

    with Console("Copying target files"):
        _image.copy()

    with Console("Configuring"):
        _image.configure()



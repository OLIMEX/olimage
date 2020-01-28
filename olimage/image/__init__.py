import click
import os

import olimage.environment as env

from .image import Image
from .parameters import parameters

__all__ = [
    'Image'
]


@click.command(name="image")
@parameters
@click.pass_context
def build_image(ctx:click.Context, **kwargs):

    kwargs['output'] = os.path.join(env.paths['images'], kwargs['output'])

    # Update env options
    env.options.update(kwargs)

    # Invoke build rootfs
    import olimage.rootfs
    ctx.invoke(olimage.rootfs.build_rootfs, **kwargs)

    image: Image = env.obj_graph.provide(Image)

    print("\n\n# Image")
    print("## Generating")
    image.generate()
    image.partition()
    image.format()
    image.bootloader()

    print("## Copying")
    image.copy(env.paths['debootstrap'])

    print("## Configuring")
    image.configure()



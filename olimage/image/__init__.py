import click
# import datetime
import os

import olimage.environment as env

from .image import Image
from .parameters import parameters

__all__ = [
    'Image'
]


def get_size(path):
    size = 0
    for dir, _, file in os.walk(path):
        for f in file:
            fp = os.path.join(dir, f)

            if not os.path.islink(fp):
                size += os.path.getsize(fp)

    return size


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
    source = env.paths['debootstrap']

    print("\nBuilding: \033[1m{}\033[0m based distribution".format(kwargs['output']))

    # Check required space
    size = max((get_size(source) >> 20) + 300, kwargs['size'])

    image: Image = env.obj_graph.provide(Image)
    image.generate(size)
    image.partition()
    image.format()
    image.configure()
    image.copy(source)



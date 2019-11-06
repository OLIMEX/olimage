import click
# import datetime
import os

import olimage.environment as env

from .image import Image

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
# Arguments
@click.argument("source")
@click.argument("output")
# Options
@click.option("--size", default=500, help="Size in MiB")
def build_image(**kwargs):

    kwargs['output'] = os.path.join(env.paths['images'], kwargs['output'])

    # Update env options
    env.options.update(kwargs)

    print("\nBuilding: \033[1m{}\033[0m based distribution".format(kwargs['output']))

    # Check required space
    size = max((get_size(kwargs['source']) >> 20) + 300, kwargs['size'])

    image: Image = env.obj_graph.provide(Image)
    image.generate(size)
    image.partition()
    image.format()
    image.configure()
    image.copy(kwargs['source'])



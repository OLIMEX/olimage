import click
import datetime

import olimage.environment as env

from .image import Image

__all__ = [
    'Image'
]


@click.command(name="image")
# Arguments
@click.argument("output", required=False)
# Options
@click.option("--size", default=500, help="Size in MiB")
def build_image(**kwargs):

    # Validate name
    if kwargs['output'] is None:
        kwargs['output'] = "olimage_{}.img".format(datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S"))
    import os
    kwargs['output'] = os.path.join(env.paths['workdir'], 'images', kwargs['output'])

    # Update env options
    env.options.update(kwargs)

    print("\nBuilding: \033[1m{}\033[0m based distribution".format(kwargs['output']))

    image: Image = env.obj_graph.provide(Image)
    image.generate(kwargs['size'])
    image.partition()
    image.format()
    image.configure()
    image.copy()



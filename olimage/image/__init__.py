import click
import os

import olimage.environment as env
import olimage.filesystem

from olimage.core.io import Console
from olimage.core.parsers import Board
from olimage.core.utils import Utils

from .image import Image
from .parameters import parameters

__all__ = [
    'Image'
]


@click.command(name="image")
@parameters
@click.pass_context
def build_image(ctx: click.Context, **kwargs):

    # Update env options
    env.options.update(kwargs)

    # Invoke build filesystem
    ctx.invoke(olimage.filesystem.build_filesystem, **kwargs)

    image = os.path.join(env.paths['images'], kwargs['output'])

    console: Console = Console()
    builder: Image = Image(image)

    if not os.path.exists(env.paths['build']):
        os.mkdir(env.paths['build'])
        Utils.archive.extract(env.paths['build'] + '.tar.gz', env.paths['build'])

    console.info("Creating image \'{}\'...".format(os.path.basename(image)))

    with Console("Generating black image"):
        builder.generate()
        builder.partition()
        builder.format()
        builder.bootloader()

    with Console("Copying target files"):
        builder.copy()

    with Console("Configuring"):
        builder.configure()

    if 'HOST_PWD' in env.env:
        realpath = env.env['HOST_PWD'] + '/' + '/'.join(image.split('/')[2:])
    else:
        realpath = image
    console.success("Your image is ready at: {}".format(realpath))



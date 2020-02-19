import click

import olimage.environment as env

from olimage.core.parsers import (Boards, Board, Distributions)
from olimage.core.io import Console

from .parameters import parameters

from .variants import (FileSystemBase, FileSystemLite)


def verify_options():

    # Verify release
    release = None

    for dist in Distributions():
        if env.options['release'] == str(dist):
            release = dist.recommended
        elif env.options['release'] in dist.releases:
            release = env.options['release']

        if release:
            env.objects['distribution'] = dist
            break

    if release is None:
        raise Exception("Target distribution \'{}\' not found in configuration files".format(release))

    if release != env.options['release']:
        Console.warning("Using distribution stable release: \'{}\'".format(release))

    env.options['release'] = release


@click.command(name="filesystem")
@parameters
def build_filesystem(**kwargs):

    # Update environment options
    env.options.update(kwargs)
    verify_options()

    # Build filesystem
    # root: Rootfs = env.obj_graph.provide(Rootfs)

    board: Board = Boards().get_board(kwargs['board'])
    env.objects['board'] = board

    builders = [FileSystemLite]
    if env.options['variant'] == "base":
        builders.append(FileSystemBase)

    for builder in builders:
        Console.info("Creating \'{}\' filesystem...".format(builder.variant.upper()))

        for stage in ['build', 'configure', 'cleanup', 'export']:
            try:
                method = getattr(builder(), stage)
            except AttributeError:
                continue

            if not callable(method):
                continue

            with Console(stage.capitalize()):
                method()


import click
import os

import olimage.environment as env

from olimage.core.parsers import (Boards, Board, Distributions)
from olimage.core.io import Console
from olimage.core.service import Service

from .parameters import parameters

from .variants import *


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
        Console().warning("Using distribution stable release: \'{}\'".format(release))

    env.options['release'] = release

    # Verify any extra files exist in overlays
    overlay_dir = env.paths['overlay']
    for file in env.options['extra_file']:
        if not os.path.isfile(f'{overlay_dir}/{file}'):
            raise Exception(f"Extra file '{file}' not found in overlays")


@click.command(name="filesystem")
@parameters
def build_filesystem(**kwargs):
    """
    Build root filesystem and configure it.
    """

    # Update environment options
    env.options.update(kwargs)
    verify_options()

    # Build filesystem
    board: Board = Boards().get_board(kwargs['board'])
    env.objects['board'] = board

    # Prepare build tree
    env.paths['board'] = os.path.join(env.paths['output'], str(board).lower())
    if not os.path.exists(env.paths['board']):
        os.mkdir(env.paths['board'])

    for directory in ['filesystem', 'images']:
        path = os.path.join(env.paths['board'], directory)

        # Create directory
        if not os.path.exists(path):
            os.mkdir(path)

        # Append paths
        env.paths[directory] = path

    builders = [VariantMinimal, VariantBase]

    for builder in builders:
        _builder = builder()

        Console().info("Creating \'{}\' filesystem...".format(_builder.variant))

        for stage in _builder.stages:
            method = getattr(_builder, stage)

            with Console(stage.capitalize()):
                method()

        # If this current stage is the target one break
        if builder.variant == env.options['variant']:
            break

    if env.options['apt_cacher']:
        Service.apt_cache.disable()

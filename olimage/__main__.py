import logging
import os
import sys

import click
import pinject

import olimage.image
import olimage.rootfs
import olimage.packages

import olimage.environment as environment


def generate_environment(**kwargs):
    """
    Generate global scope environment

    :param kwargs: kwargs to be added
    :return: None
    """

    # Add paths
    root = os.path.dirname(os.path.abspath(__file__))
    environment.paths.update({
        'root' : root,
        'configs' : os.path.join(os.path.dirname(root), kwargs['configs']),
        'overlay': os.path.join(os.path.dirname(root), kwargs['overlay']),
        'workdir' : os.path.join(os.path.dirname(root), kwargs['workdir']),
    })

    # Copy command-line parameters to global env
    environment.options.update(kwargs)

    # Setup environment variables
    environment.env.update(os.environ.copy())
    environment.env['LC_ALL'] = 'C'
    environment.env['LANGUAGE'] = 'C'
    environment.env['LANG'] = 'C'
    environment.env['DEBIAN_FRONTEND'] = 'noninteractive'
    environment.env['DEBCONF_NONINTERACTIVE_SEEN'] = 'true'


def prepare_logging():
    """
    Configure logging module

    :return: None
    """
    if environment.options['log'] is None:
        return

    logging.basicConfig(
        filename=environment.options['log'],
        filemode='w',
        format='\033[1m%(name)s\033[0m | %(message)s',
        level=logging.DEBUG if environment.options['verbose'] > 0 else logging.INFO)


def prepare_tree():
    """
    Prepare build directory structure

    :return: None
    """

    # Check required directory structure
    workdir = environment.paths['workdir']
    if not os.path.exists(workdir):
        os.mkdir(workdir)

    for directory in ['dl', 'build', 'rootfs', 'images']:
        path = os.path.join(workdir, directory)

        # Create directory
        if not os.path.exists(path):
            os.mkdir(path)

        # Append paths
        environment.paths[directory] = path


@click.group()
# Options
@click.option("--workdir", default="output", help="Specify working directory.")
@click.option("--configs", default="configs", help="Configs directory")
@click.option("--overlay", default="overlay", help="Path to overlay files")
@click.option("-v", "--verbose", count=True, help="Increase logging verbosity.")
@click.option("--apt-cacher/--no-apt-cacher",
              default=True,
              help="Use apt-cacher service")
@click.option("--apt-cacher-host",
              default=lambda: os.environ.get('APT_CACHER_HOST', '172.17.0.1'),
              help="Specify apt-cache service host")
@click.option("--apt-cacher-port",
              default=lambda: int(os.environ.get('APT_CACHER_PORT', '31420')),
              type=int,
              help="Specify apt-cache service port")
@click.option("--log",
              help="Logging file.")
def cli(**kwargs):
    generate_environment(**kwargs)
    prepare_logging()
    prepare_tree()

    environment.obj_graph = pinject.new_object_graph()


# # Add sub-commands
cli.add_command(olimage.packages.build_packages)
cli.add_command(olimage.rootfs.build_rootfs)
cli.add_command(olimage.image.build_image)


@cli.command()
# Arguments
@click.argument("board")
@click.argument("release")
@click.argument("variant", type=click.Choice(['minimal', 'base', 'full']))
@click.argument("output")
# Options
@click.option("--overlay", default="overlay", help="Path to overlay files")
@click.pass_context
def test(ctx: click.Context, **kwargs):

    from olimage.core.parsers import Boards, Board, Bootloader
    from olimage.core.utils import Utils

    # Update environment options
    environment.options.update(kwargs)

    # Build rootfs
    ctx.invoke(olimage.rootfs.build_rootfs, **kwargs)

    # Install packages
    ctx.invoke(olimage.packages.build_packages, board=kwargs['board'], package=None, command='install')

    # Build image
    ctx.invoke(olimage.image.build_image, source=environment.paths['debootstrap'], output=kwargs['output'])

    # Install bootloader
    _boards: Boards = environment.obj_graph.provide(Boards)
    _board: Board = _boards.get_board(kwargs['board'])
    _bootloader: Bootloader = _board.bootloader

    Utils.shell.run(
        'dd if={} of={} conv=notrunc,fsync bs={} seek={}'.format(
            environment.paths['debootstrap'] + _bootloader.file,
            environment.options['output'],
            _bootloader.block,
            _bootloader.offset))


if __name__ == "__main__":
    sys.exit(cli())
    # try:
    #     sys.exit(cli())
    # except Exception as e:
    #     print(e)
    #     sys.exit(1)
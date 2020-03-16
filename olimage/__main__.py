import logging
import os
import sys
import traceback

import click
import pinject

import olimage.image
import olimage.filesystem

import olimage
import olimage.environment as environment

from olimage.core.io import Console
from olimage.core.utils import Utils


def prepare_logging():
    """
    Configure logging module

    :return: None
    """

    if environment.options['verbose']:
        logging.basicConfig(
            format='%(message)s',
            level=logging.DEBUG,
            handlers=[logging.StreamHandler(sys.stdout)]
        )

    if environment.options['log']:
        logging.basicConfig(
            filename=environment.options['log'],
            filemode='w',
            format='%(message)s',
            level=logging.DEBUG,
        )


def prepare_tree():
    """
    Prepare build directory structure

    :return: None
    """

    # Check required directory structure
    output = environment.paths['output']
    if not os.path.exists(output):
        os.mkdir(output)


@click.group()
@click.option("--output", help="Specify output directory")
# Apt-cacher
@click.option("--apt-cacher/--no-apt-cacher",
              default=False,
              help="Use apt-cacher service")
@click.option("--apt-cacher-host",
              default=lambda: os.environ.get('APT_CACHER_HOST', '127.0.0.1'),
              help="Specify apt-cache service host")
@click.option("--apt-cacher-port",
              default=lambda: int(os.environ.get('APT_CACHER_PORT', '3142')),
              type=int,
              help="Specify apt-cache service port")
# Logging
@click.option("-v", "--verbose", is_flag=True, help="Increase logging verbosity.")
@click.option("-r", "--releaseimage", is_flag=True, help="Build release image (do not use staging repository).")
@click.option("--log",
              help="Logging file.")
@click.option("-V", "--version", is_flag=True, help="Show the current package version")
def cli(**kwargs):
    """
    Build system for the OLinuXino boards
    \f

    :param kwargs:
    :return:
    """

    # Check for package version
    if kwargs['version']:
        print("olimage: {}".format(olimage.__version__))
        sys.exit(0)

    # Update environment
    environment.options.update(kwargs)

    if kwargs['output']:
        environment.paths['output'] = kwargs['output']

    prepare_logging()
    prepare_tree()

    # Initialize the object graph
    environment.obj_graph = pinject.new_object_graph()


@cli.command(name="clean")
def clean():
    """
    Remove all files in the OUTPUT folder.
    \f

    :return:
    """
    Utils.shell.run('rm -rf {}/*'.format(environment.paths['output']), shell=True)


# Add external sub-commands
cli.add_command(olimage.filesystem.build_filesystem)
cli.add_command(olimage.image.build_image)


if __name__ == "__main__":
    try:
        sys.exit(cli())
    except Exception as e:
        # Print the exception traceback
        traceback.print_exc()
        Console().error(str(e))
        sys.exit(1)

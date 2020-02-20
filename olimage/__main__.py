import logging
import os
import sys
import traceback

import click
import pinject
import shutil

import olimage.image
import olimage.filesystem

import olimage
import olimage.environment as environment

from olimage.core.io import Console

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
        format='%(message)s',
        level=logging.DEBUG if environment.options['verbose'] > 0 else logging.INFO)


def prepare_tree():
    """
    Prepare build directory structure

    :return: None
    """

    # Check required directory structure
    output = environment.paths['output']
    if not os.path.exists(output):
        os.mkdir(output)

    for directory in ['filesystem', 'images']:
        path = os.path.join(output, directory)

        # Create directory
        if not os.path.exists(path):
            os.mkdir(path)

        # Append paths
        environment.paths[directory] = path


@click.group()
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
@click.option("-v", "--verbose", count=True, help="Increase logging verbosity.")
@click.option("--log",
              help="Logging file.")
@click.option("-V", "--version", is_flag=True, help="Show the current package version")
def cli(**kwargs):

    # Check for package version
    if kwargs['version']:
        print("olimage: {}".format(olimage.__version__))
        sys.exit(0)

    # Update environment
    environment.options.update(kwargs)

    prepare_logging()
    prepare_tree()

    # Initialize the object graph
    environment.obj_graph = pinject.new_object_graph()


@cli.command(name="clean")
def clean():
    shutil.rmtree(environment.paths['output'])


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

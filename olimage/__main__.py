#!/usr/env/bin python3

import logging
import os
import sys

import click
import yaml




from .bsp import BSP
from .debootstrap import Debootstrap

from olimage.board import Board
import olimage.environment as environment



def find_target(target):
    """
    Search for target board in configurations

    :param target: board name
    :return:
    """
    boards = os.path.dirname(__file__)
    print(boards)

def generate_environment(**kwargs):
    """
    Generate global scope environment

    :param kwargs: kwargs to be added
    :return: None
    """

    # Add paths
    root = os.path.dirname(os.path.abspath(__file__))
    environment.env.update({
        'paths': {
            'root' : root,
            'configs' : os.path.join(root, 'configs')
        }
    })

    # Copy command-line parameters to global env
    environment.env.update(kwargs)

    # Setup environment variables
    # environment.env.update(os.environ.copy())
    # environment.env['LC_ALL'] = 'C'
    # environment.env['LANGUAGE'] = 'C'
    # environment.env['LANG'] = 'C'
    # environment.env['DEBIAN_FRONTEND'] = 'noninteractive'
    # environment.env['DEBCONF_NONINTERACTIVE_SEEN'] = 'true'


def prepare_logging():
    """
    Configure logging module

    :return: None
    """
    if environment.env['log'] is None:
        return

    logging.basicConfig(
        filename=environment.env['log'],
        filemode='w',
        format='\033[1m%(name)s\033[0m | %(message)s',
        level=logging.DEBUG if environment.env['verbose'] > 0 else logging.INFO)


def prepare_tree():
    """
    Prepare build directory structure

    :return: None
    """

    # Get working directory
    workdir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        environment.env['workdir'])

    # Check required directory structure
    if not os.path.exists(workdir):
        os.mkdir(workdir)
    for d in ['dl', 'build', 'rootfs']:
        if not os.path.exists(os.path.join(workdir, d)):
            os.mkdir(os.path.join(workdir, d))


@click.command()

# Options
@click.option("-w", "--workdir", default="output", help="Specify working directory.")
@click.option("-v", "--verbose", count=True, help="Increase loggging verbosity.")
@click.option("--log", help="Logging file.")

# Arguments
@click.argument("target")
@click.argument("release")
def cli(**kwargs):

    generate_environment(**kwargs)
    prepare_logging()
    prepare_tree()

    # Generate board object
    b = Board(kwargs['target'])
    print(b)


#
# @cli.command(name="build")
# @click.argument("target", help="123131")
# @click.argument("board")
# def build_command(target, board):
#
#     # Search config file
#
#
#     # Parse config file
#     with open('/home/stefan/Desktop/builder/configs/boards/a64-olinuxino.yaml', 'r') as f:
#         config = yaml.full_load(f.read())
#
#     d = Debootstrap(config['arch'], target).build()
#     return
#
#
#     # Check BSP
#     try:
#         bsp_config = config['bsp']
#     except KeyError as e:
#         raise KeyError("Missing mandatory key in config file: {}".format(e))
#
#     board_packages = {}
#
#     for key in config['bsp']:
#         obj = BSP.generate(key, bsp_config, **ctx.obj)
#         if obj:
#             board_packages[key] = obj
#
#
#     # TODO: This needs serious work!
#     build_order = []
#     for name, obj in board_packages.items():
#
#         # Check dependency
#         for dep in obj.dependency:
#             if dep in board_packages and board_packages[dep] not in build_order:
#                 build_order += [board_packages[dep]]
#         if obj not in build_order:
#             build_order += [obj]
#
#     # Build packager
#     for pkg in build_order:
#         pkg.build()
#     return
#
#     # Parse config
#     if 'u-boot' not in self._config:
#         raise Exception("There is no \'u-boot\' object in {}".format(self._file))
#     self._config = self._config['u-boot']
#
#     if 'source' not in self._config:
#         raise Exception("Missing \'source\' object in {}".format(self._file))
#
#     # u = Uboot(, **ctx.obj)
#     # u.build()
#
#     pass
#     # w = Worker()
#     # w.run("ls -l")
#     # Build u-boot
#     # u = Uboot()
#     # u.configure().build()
#
#     # Generate rootfs
#     # deb = Debootstrap()
#     # deb.build(release)
#
# # @cli.command(name="uboot")
# # @click.pass_context
# # def build_uboot(ctx):
# #     return
# #     u = Uboot('/home/stefan/Desktop/builder/configs/boards/a64-olinuxino.yaml', **ctx.obj)
#     # u.configure().build()



if __name__ == "__main__":
    sys.exit(cli())
    try:
        sys.exit(cli())
    except Exception as e:
        print("    {}".format(e))
        sys.exit(1)
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Olimex Ltd.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging
import os
import sys

import click

from olimage.board import Board
from olimage.debootstrap import Debootstrap

import olimage.environment as environment
import olimage.packages as package


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
    environment.paths.update({
            'root' : root,
            'configs' : os.path.join(root, 'configs'),
            'workdir' : os.path.join(root, kwargs['workdir']),
            'overlay' : os.path.join(root, kwargs['overlay'])
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

    for d in ['dl', 'build', 'rootfs', 'images']:
        if not os.path.exists(os.path.join(workdir, d)):
            os.mkdir(os.path.join(workdir, d))


@click.group()
# Options
@click.option("-w", "--workdir", default="output", help="Specify working directory.")
@click.option("--overlay", default="overlay", help="Path to overlay files")
@click.option("-v", "--verbose", count=True, help="Increase logging verbosity.")
@click.option("--log", help="Logging file.")
def cli(**kwargs):

    generate_environment(**kwargs)
    prepare_logging()
    prepare_tree()

    return

    # Generate board object
    b = Board(kwargs['target'])

    # Build board packages
    board_packages = {}
    for key, value in b.packages.items():
        try:
            obj = package.Pool[key]
            board_packages[key] = obj(value)
        except KeyError as e:
            raise Exception("Missing package builder: {}".format(e))

    for key, value in board_packages.items():
        print("\nBuilding: \033[1m{}\033[0m".format(key))
        value.download().configure().build().package().install()

    return


@cli.command(name="rootfs")
# Arguments
@click.argument("target")
@click.argument("release")
def build_rootfs(**kwargs):

    # Update environment options
    environment.options.update(kwargs)

    # Generate board object
    b = Board(kwargs['target'])

    # Build rootfs
    d = Debootstrap(b, kwargs['release']).build()

    # Generate empty target image
    d.generate().partition()

    # Create filesystems
    d.format()

    # Make final configurations
    d.configure()

    # Copy rootfs files to the image
    # d.copy()


@cli.command(name="package")
# Options
@click.option("--step", type=click.Choice(['download', 'configure', 'build', 'package']), default='package')
# Arguments
@click.argument("target")
@click.argument("package")
def build_package(**kwargs):

    # Update environment options
    environment.options.update(kwargs)

    # Generate board object
    b = Board(kwargs['target'])

    # Build board packages
    board_packages = {}
    for key, value in b.packages.items():
        try:
            obj = package.Pool[key]
            board_packages[key] = obj(value)
        except KeyError as e:
            raise Exception("Missing package builder: {}".format(e))

    obj = board_packages[kwargs['package']]  # type: package.Package

    step = kwargs['step']

    obj.download()
    if step == 'download':
        return

    obj.configure()
    if step == 'configure':
        return

    obj.build()
    if step == 'build':
        return

    obj.package()

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
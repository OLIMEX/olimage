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
import pinject

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
        'workdir' : os.path.join(os.path.dirname(root), kwargs['workdir'])
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
@click.option("--workdir", default="output", help="Specify working directory.")
@click.option("--configs", default="configs", help="Configs directory")
@click.option("--overlay", default="overlay", help="Path to overlay files")
@click.option("-v", "--verbose", count=True, help="Increase logging verbosity.")
@click.option("--log", help="Logging file.")
def cli(**kwargs):
    generate_environment(**kwargs)
    prepare_logging()
    prepare_tree()

    environment.obj_graph = pinject.new_object_graph()


# # Add sub-commands
cli.add_command(olimage.packages.build_packages)
cli.add_command(olimage.rootfs.build_rootfs)


# @cli.command()
# # Arguments
# @click.argument("target")
# @click.argument("release")
# @click.argument("variant", type=click.Choice(['minimal', 'base', 'full']))
# # Options
# @click.option("--overlay", default="overlay", help="Path to overlay files")
# def test(**kwargs):
#
#     # Update environment options
#     environment.options.update(kwargs)
#
#     # Generate board object
#     environment.board = Board(kwargs['target'])
#     b = environment.board
#
#     # Build rootfs
#     d = olimage.rootfs.debootstrap.Builder.debootstrap(**kwargs)
#     d.build()
#
#     # Generate empty target image
#     d.generate().partition()
#
#     # Create filesystems
#     d.format()
#
#     # Make final configurations
#     d.configure()
#
#     # Build board packages
#     board_packages = {}
#     for key, value in b.packages.items():
#         try:
#             obj = olimage.packages.Pool[key]
#             board_packages[key] = obj(value)
#         except KeyError as e:
#             raise Exception("Missing package builder: {}".format(e))
#
#     # Generate package worker
#     worker = olimage.packages.Package(board_packages)
#
#     for p in worker.packages:
#         for key, value in p.items():
#             print("\nBuilding: \033[1m{}\033[0m".format(key))
#             worker.run(key, 'install')
#
#     print("\nBuilding: \033[1m{Image}\033[0m")
#     d.copy()


if __name__ == "__main__":
    sys.exit(cli())
    try:
        sys.exit(cli())
    except Exception as e:
        print("    {}".format(e))
        sys.exit(1)
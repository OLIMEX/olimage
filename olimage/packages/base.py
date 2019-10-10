import importlib
import inspect
import pkgutil
import os

import click

from .package import (Package, PackageBase)

from olimage.board import Board
import olimage.environment as env


# Scan for package modules
Pool = {}
for (path, dirs, files) in os.walk(os.path.dirname(__file__)):
    for d in dirs:
        for (_, name, _) in pkgutil.walk_packages([os.path.join(path, d)]):
            # Import module
            module = importlib.import_module('olimage.packages.' + d + '.' + name)

            # Get all classes
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, PackageBase) and cls != PackageBase:
                    try:
                        Pool[cls.alias()] = cls
                    except NotImplementedError:
                        pass
                    except AttributeError:
                        pass


@click.command(name="packages")
# Arguments
@click.argument("board")
@click.argument("package", required=False)
@click.argument("command", required=False, default="package",
                type=click.Choice(['download', 'configure', 'build', 'package', 'install']))
def build_package(**kwargs):

    # Update env options
    env.options.update(kwargs)

    # Generate board object
    env.board = Board(kwargs['board'])
    b = env.board

    # Build board packages
    board_packages = {}
    for key, value in b.packages.items():
        try:
            obj = Pool[key]
            board_packages[key] = obj(value)
        except KeyError as e:
            raise Exception("Missing package builder: {}".format(e))

    # Generate package worker
    worker = Package(board_packages)

    if kwargs['package'] is None:
        for p in worker.packages:
            for key,value in p.items():
                print("\nBuilding: \033[1m{}\033[0m".format(key))
                worker.run(key, kwargs['command'])
    else:
        print("\nBuilding: \033[1m{}\033[0m".format(kwargs['package']))
        worker.run(kwargs['package'], kwargs['command'])

import importlib
import inspect
import pkgutil
import os

import click

import olimage.environment as env

from .package import (Packages, AbstractPackage)

# Scan for package modules
board_packages = {}
for (path, dirs, files) in os.walk(os.path.dirname(__file__)):
    for d in dirs:
        for (_, name, _) in pkgutil.walk_packages([os.path.join(path, d)]):
            # Import module
            module = importlib.import_module('olimage.packages.' + d + '.' + name)

            # Get all classes
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, AbstractPackage) and cls != AbstractPackage:
                    try:
                        board_packages[cls.alias()] = cls
                    except NotImplementedError:
                        pass


@click.command(name="packages")
# Arguments
@click.argument("board")
@click.argument("command", required=False, default="package",
    type=click.Choice(['download', 'patch', 'configure', 'build', 'package', 'install']))
@click.argument("package", required=False)
def build_packages(**kwargs):

    # Update env options
    env.options.update(kwargs)

    # Generate package worker
    worker = Packages({key:env.obj_graph.provide(value) for (key,value) in board_packages.items()})

    if kwargs['package'] is None:
        for p in worker.packages:
            for key,value in p.items():
                print("\nBuilding: \033[1m{}\033[0m".format(key))
                worker.run(key, kwargs['command'])
    else:
        print("\nBuilding: \033[1m{}\033[0m".format(kwargs['package']))
        worker.run(kwargs['package'], kwargs['command'])

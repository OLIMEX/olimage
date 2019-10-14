import importlib
import inspect
import pkgutil
import os


import click
import pinject

from dependency_injector import containers, providers

from .package import (Packages, PackageBase)

from olimage.board import Board
from olimage.container import IocContainer
import olimage.environment as env


# Scan for package modules
board_packages = {}
for (path, dirs, files) in os.walk(os.path.dirname(__file__)):
    for d in dirs:
        for (_, name, _) in pkgutil.walk_packages([os.path.join(path, d)]):
            # Import module
            module = importlib.import_module('olimage.packages.' + d + '.' + name)

            # Get all classes
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, PackageBase) and cls != PackageBase:
                    board_packages[cls.alias()] = cls
                    try:
                        deps = {}
                        for arg in inspect.getargspec(cls.__init__).args:
                            # Skip self argument
                            if arg == 'self':
                                continue

                            # Check if arg can be injected
                            try:
                                deps[arg] = getattr(IocContainer, arg)
                            except AttributeError:
                                continue


                        # if len(deps):
                        #     print(cls)
                        #     setattr(Builder, name, providers.Factory(cls, board=IocContainer.board))
                        # else:
                        #     setattr(Builder, name, providers.Factory(cls, bossard=IocContainer.board))
                            # setattr(Builder, name, providers.Factory(cls))

                    except NotImplementedError:
                        pass

# print(board_packages)
# print(board_packages)

class Builder(containers.DeclarativeContainer):
    package = providers.Factory(Packages)

    uboot = providers.Factory(board_packages['u-boot'], board=1111)


@click.command(name="packages")
# Arguments
@click.argument("board")
@click.argument("package", required=False)
@click.argument("command", required=False, default="package",
                type=click.Choice(['download', 'configure', 'build', 'package', 'install']))
def build_package(**kwargs):

    # Update env options
    env.options.update(kwargs)

    # print(dir(Builder))
    print(Builder.uboot())
    # print(Builder.uboot())

    # # Generate board object
    # env.board = Board(kwargs['board'])
    # b = env.board

    # # Build board packages
    # board_packages = {}
    # for key, value in b.packages.items():
    #     try:
    #         obj = Pool[key]
    #         board_packages[key] = obj(value)
    #     except KeyError as e:
    #         raise Exception("Missing package builder: {}".format(e))

    # Generate package worker
    # worker = Package(board_packages)
    # print(board_packages)
    # package = Builder.package(board_packages)

    # from olimage.core.parsers import Board
    # b = Board(kwargs['board'])
    #
    # print('u-boot' in [str(x) for x in b.packages])
    #
    # print(b.packages)
    # for p in b.packages:
    #     print(p)
    #     print(p.source)
    # # print(b)
    # # print(iter(b))
    #
    # print(dir(Builder))
    # uboot = Builder.uboot()
    # print(uboot)

    import sys
    sys.exit(0)

    #
    # if kwargs['package'] is None:
    #     for p in worker.packages:
    #         for key,value in p.items():
    #             print("\nBuilding: \033[1m{}\033[0m".format(key))
    #             worker.run(key, kwargs['command'])
    # else:
    #     print("\nBuilding: \033[1m{}\033[0m".format(kwargs['package']))
    #     worker.run(kwargs['package'], kwargs['command'])

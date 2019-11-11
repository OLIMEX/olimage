import click

import olimage.environment as env

from .rootfs import Rootfs

__all__ = [
    'Rootfs'
]


@click.command(name="rootfs")
# Arguments
@click.argument("board")
@click.argument("release")
@click.argument("variant", type=click.Choice(['minimal', 'base', 'full']))
# Options
@click.option("--hostname", help="Set default system hostname")
@click.option("--locale", default="en_GB.UTF-8", help="Set default system locale")
@click.option("--timezone", default="Europe/London", help="Set default system timezone")
def build_rootfs(**kwargs):

    # Update environment options
    env.options.update(kwargs)

    # Build rootfs
    rootfs: Rootfs = env.obj_graph.provide(Rootfs)

    print("\nBuilding: \033[1m{}\033[0m based distribution".format(kwargs['release']))
    rootfs.build()
    rootfs.configure()
    rootfs.cleanup()
import click
import os

import olimage.environment as env

from .debootstrap import Debootstrap, Builder
from .distributions import Distribution
from .mounter import Map, Mount
from .partitions import Partitions


class ORM(object):
    def __init__(self, name, data):
        self._name = name
        self._data = data

    def __str__(self):
        return self._name

    def __getattr__(self, item):
        # Check if item is in the config dict
        if item not in self._data:
            raise AttributeError("\'{}\' object has no attribute \'{}\'".format(self.__class__.__name__, item))

        # If data[item] is dictionary create new ORM object
        if isinstance(self._data[item], dict):
            return ORM(item, self._data[item])

        # Return value
        return self._data[item]


@click.command(name="rootfs")
# Arguments
@click.argument("target")
@click.argument("release")
@click.argument("variant", type=click.Choice(['minimal', 'base', 'full']))
# Options
@click.option("--overlay", default="rootfs/overlay", help="Path to overlay files")
def build_rootfs(**kwargs):

    # Update environment options
    env.options.update(kwargs)
    env.paths['overlay'] = os.path.join(env.paths['root'], kwargs['overlay'])

    # Build rootfs
    d = Builder.debootstrap(**kwargs)
    d.build()

    # Generate empty target image
    d.generate().partition()

    # Create filesystems
    d.format()

    # Make final configurations
    d.configure()

    # Copy rootfs files to the image
    d.copy()
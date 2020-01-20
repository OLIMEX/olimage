import click

from olimage.rootfs.parameters import _arguments, _options

_arguments += [
    click.argument("output")
]

_options += [
    click.option("--size", default=500, help="Size in MiB")
]


def parameters(func):
    for argument in reversed(_arguments):
        func = argument(func)

    for option in reversed(_options):
        func = option(func)

    return func

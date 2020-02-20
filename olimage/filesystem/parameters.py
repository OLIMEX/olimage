import click

from olimage.core.parsers.packages import ParserPackages

_arguments = [
    click.argument("board"),
    click.argument("release"),
    click.argument("variant", type=click.Choice([str(v) for v in ParserPackages().variants]))
]

_options = [
    click.option("--hostname", help="Set default system hostname"),
    click.option("--keyboard-keymap", default="gb", help="Set default system keyboard locale"),
    click.option("--keyboard-layout", default="English (UK)", help="Set default system keyboard locale"),
    click.option("--locale", default="en_GB.UTF-8", help="Set default system locale"),
    click.option("--ssh/--no-ssh", default=True, help="Enable/Disable ssh access"),
    click.option("--timezone", default="Europe/London", help="Set default system timezone")
]


def parameters(func):
    for argument in reversed(_arguments):
        func = argument(func)

    for option in reversed(_options):
        func = option(func)

    return func

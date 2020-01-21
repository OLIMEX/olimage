import logging
import os
import sys

import click
import pinject
import shutil

import olimage.image
import olimage.rootfs

import olimage
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
        'workdir' : os.path.join(os.path.dirname(root), kwargs['workdir']),
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

    for directory in ['dl', 'build', 'rootfs', 'images']:
        path = os.path.join(workdir, directory)

        # Create directory
        if not os.path.exists(path):
            os.mkdir(path)

        # Append paths
        environment.paths[directory] = path


@click.group()
# Options
@click.option("--workdir", default="output", help="Specify working directory.")
@click.option("--configs", default="configs", help="Configs directory")
@click.option("--overlay", default="overlay", help="Path to overlay files")
# Apt-cacher
@click.option("--apt-cacher/--no-apt-cacher",
              default=False,
              help="Use apt-cacher service")
@click.option("--apt-cacher-host",
              default=lambda: os.environ.get('APT_CACHER_HOST', '127.0.0.1'),
              help="Specify apt-cache service host")
@click.option("--apt-cacher-port",
              default=lambda: int(os.environ.get('APT_CACHER_PORT', '3142')),
              type=int,
              help="Specify apt-cache service port")
# Logging
@click.option("-v", "--verbose", count=True, help="Increase logging verbosity.")
@click.option("--log",
              help="Logging file.")
@click.option("-V", "--version", is_flag=True, help="Show the current package version")
def cli(**kwargs):

    # Check for package version
    if kwargs['version']:
        print("olimage: {}".format(olimage.__version__))
        sys.exit(0)

    # Generate environment and tree
    generate_environment(**kwargs)
    prepare_logging()
    prepare_tree()

    # Initialize the object graph
    environment.obj_graph = pinject.new_object_graph()


@cli.command(name="clean")
def clean():
    shutil.rmtree(environment.paths['workdir'])

# Add external sub-commands
cli.add_command(olimage.rootfs.build_rootfs)
cli.add_command(olimage.image.build_image)




# @cli.command()
# # Arguments
# @click.argument("board")
# @click.argument("release")
# @click.argument("variant", type=click.Choice(['lite', 'base', 'full']))
# @click.argument("output")
# @click.pass_context
# def test(ctx: click.Context, **kwargs):
#
#     from olimage.core.parsers import Boards, Board, Bootloader
#     from olimage.core.utils import Utils
#
#     # Update environment options
#     environment.options.update(kwargs)
#
#     # Build rootfs
#     ctx.invoke(olimage.rootfs.build_rootfs, **kwargs)
#
#     # Install packages
#     # ctx.invoke(olimage.packages.build_packages, board=kwargs['board'], package=None, command='install')
#
#     # Build image
#     ctx.invoke(olimage.image.build_image, source=environment.paths['debootstrap'], output=kwargs['output'])
#
#     # Install bootloader
#     _boards: Boards = environment.obj_graph.provide(Boards)
#     _board: Board = _boards.get_board(kwargs['board'])
#
#     # Install SPL
#     spl: Bootloader
#     spl = _board._data['bootloaders']['spdl']
#     Utils.shell.run(
#             'dd if={} of={} conv=notrunc,fsync bs={} seek={}'.format(
#                 environment.paths['debootstrap'] + spl['file'], environment.options['output'], spl['block'], spl['offset'])
#     )
#
#     # Install u-boot
#     u_boot: Bootloader
#     u_boot = _board._data['bootloaders']['u-boot']
#     temp = Utils.shell.run('mktemp -d').decode().strip()
#     Utils.shell.run('cp -vf {}/usr/lib/arm-trusted-firmware/sun50i_a64/bl31.bin {}/'.format(environment.paths['debootstrap'], temp))
#     Utils.shell.run('cp -vf {}/usr/lib/u-boot/a64-olinuxino/sun50i-a64-olinuxino.dtb {}/'.format(environment.paths['debootstrap'], temp))
#     Utils.shell.run('cp -vf {}/usr/lib/u-boot/a64-olinuxino/u-boot-nodtb.bin {}/'.format(environment.paths['debootstrap'], temp))
#     Utils.shell.run('cp -vf {}/usr/lib/u-boot/a64-olinuxino/u-boot.bin {}/'.format(environment.paths['debootstrap'], temp))
#     Utils.shell.run('cp -vf {}/usr/bin/mksunxi_fit_atf {}/'.format(environment.paths['debootstrap'], temp))
#     Utils.shell.run(
#         'cd {} && bash mksunxi_fit_atf *.dtb > u-boot.its && mkimage -f u-boot.its u-boot.itb'.format(temp),
#         shell=True
#     )
#
#     Utils.shell.run(
#         'dd if={} of={} conv=notrunc,fsync bs={} seek={}'.format(
#             os.path.join(temp, u_boot['file']), environment.options['output'], u_boot['block'], u_boot['offset'])
#     )
#
#     Utils.shell.run('rm -rvf {}'.format(temp))


if __name__ == "__main__":
    sys.exit(cli())
    # try:
    #     sys.exit(cli())
    # except Exception as e:
    #     print(e)
    #     sys.exit(1)
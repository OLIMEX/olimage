import datetime
import os
import uuid

import olimage.environment as env

from olimage.core.io import Console
from olimage.core.parsers.boards import Board
from olimage.core.parsers import Partitions
from olimage.core.utils import Utils


class SetupBoot(object):
    @staticmethod
    def generate_uboot_env(configs: dict = None) -> None:
        with Console("Generating /boot/uEnv.txt"):
            Utils.install('/boot/uEnv.txt')
            Utils.template.install(
                env.paths['debootstrap'] + '/boot/uEnv.txt',
                configs=configs,
                stamp={
                    'date': str(datetime.datetime.now()),
                    'uuid': str(uuid.uuid4()),
                }
            )

    @staticmethod
    def generate_boot_cmd(board: Board) -> None:
        with Console("Generating /boot/boot.scr"):
            Utils.install('/boot/boot.cmd')

            # The FIT image is always located in /boot directory.
            # If there is such defined partition retrieve it's number. Do the same for /
            parts = {
                'boot': 1,
                'root': 1
            }
            # for i in range(len(partitions)):
            #     partition = partitions[i]
            #     if partition.fstab.mount == '/':
            #         parts['root'] = i + 1
            #     elif partition.fstab.mount == '/boot':
            #         parts['boot'] = i + 1

            # Generate template
            Utils.template.install(
                env.paths['debootstrap'] + '/boot/boot.cmd',
                arch=board.arch,
                bootargs={
                    'console': 'ttyS0,115200',
                    'panic': 10,
                    'loglevel': 4,
                },
                fit={
                    'file': 'kernel.itb',
                    'load': board.loading.fit,
                },
                partitions=parts,
                stamp={
                    'date': str(datetime.datetime.now()),
                    'uuid': str(uuid.uuid4()),
                }
            )

            # Generate boot.scr
            Utils.shell.run(
                "mkimage -C none -A arm -T script -d {rootfs}/boot/boot.cmd {rootfs}/boot/boot.scr".format(
                    rootfs=env.paths['debootstrap']),
                shell=True
            )

    @staticmethod
    def generate_fit(board):
        with Console("Generating /usr/lib/olinuxino/kernel.its"):
            Utils.install('/etc/kernel/postinst.d/uboot-fit', mode='755')
            Utils.install('/usr/lib/olinuxino/kernel.its')

            # Generate fdts and overlay data
            fdts = []
            overlays = []
            for model in board.models:
                if model.fdt not in fdts:
                    fdts.append(model.fdt)

                for overlay in model.overlays:
                    file = env.paths['debootstrap'] + '/usr/lib/olinuxino-overlays/{}/{}'.format(board.soc, overlay)
                    if overlay not in overlays and os.path.exists(file):
                        overlays.append(overlay)

            # Remap board fdt and overlays
            models = []
            for model in board.models:
                dtbo = []
                for overlay in model.overlays:
                    if overlay in overlays:
                        dtbo.append(overlays.index(overlay) + 1)

                models.append({
                    'name': str(model),
                    'fdt': fdts.index(model.fdt) + 1,
                    'id': model.id,
                    'overlays': dtbo,
                    'compatible': 'olimex,{}'.format(str(model).lower())
                })

            # Generate load addresses for overlays
            addr = int(board.loading.overlays, 16)
            temp = []
            for overlay in overlays:
                temp.append({overlay: {'load': '0x{:08X}'.format(addr)}})
                addr += 0x10000
            overlays = temp

            Utils.template.install(
                env.paths['debootstrap'] + '/usr/lib/olinuxino/kernel.its',
                arch='arm' if board.arch == 'armhf' else board.arch,
                board=board,
                fdts=fdts,
                overlays=overlays,
                stamp={
                    'date': str(datetime.datetime.now()),
                    'uuid': str(uuid.uuid4()),
                },
                models=models,
            )

    @staticmethod
    def __call__(board: Board, partitions: Partitions):
        SetupBoot.generate_uboot_env()
        SetupBoot.generate_boot_cmd(board)
        SetupBoot.generate_fit(board)


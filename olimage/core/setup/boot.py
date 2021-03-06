import datetime
import os
import uuid

import olimage.environment as env

from olimage.core.io import Console
from olimage.core.parsers.boards import Board
from olimage.core.utils import Utils

from .base import SetupAbstract


class SetupBoot(SetupAbstract):
    @staticmethod
    def _generate_uboot_env(board: Board, configs: dict = None) -> None:
        with Console("Generating /boot/uEnv.txt"):
            Utils.install('/boot/uEnv.txt')
            Utils.template.install(
                env.paths['build'] + '/boot/uEnv.txt',
                configs=configs,
                stamp={
                    'date': str(datetime.datetime.now()),
                    'uuid': str(uuid.uuid4()),
                }
            )

        with Console("Installing /etc/fw_env.config"):
            Utils.install('/etc/fw_env.config')

        with Console("Installing /uboot.env"):
            src = env.paths['build'] + "/usr/lib/u-boot-olinuxino/{}/uboot.env".format(board.name.lower())
            dest = env.paths['build'] + "/uboot.env"
            Utils.shell.run('install -D -v -m {} {} {}'.format(644, src, dest))

    @staticmethod
    def _generate_boot_cmd(board: Board) -> None:
        with Console("Generating /boot/boot.scr"):
            Utils.install('/boot/boot.cmd')

            # The FIT image is always located in /boot directory.
            # If there is such defined partition retrieve it's number. Do the same for /
            parts = {
                'boot': 1,
                'root': 1
            }
            if board.soc == "stm32mp1xx":
                parts = {
                    'boot': 4,
                    'root': 4
                }

            # for i in range(len(partitions)):
            #     partition = partitions[i]
            #     if partition.fstab.mount == '/':
            #         parts['root'] = i + 1
            #     elif partition.fstab.mount == '/boot':
            #         parts['boot'] = i + 1

            # Generate template
            bootargs={
                'console': 'ttyS0,115200',
                'panic': 10,
                'loglevel': 4,
            }
            if board.soc == "stm32mp1xx":
                bootargs={
                    'console': 'ttySTM0,115200',
                    'panic': 10,
                    'loglevel': 10,
                }
            Utils.template.install(
                env.paths['build'] + '/boot/boot.cmd',
                board=board,
                bootargs=bootargs,
                fit={
                    'file': 'kernel.itb',
                    'load': board.loading.fit,
                },
                partitions=parts,
                stamp={
                    'date': str(datetime.datetime.now()),
                    'uuid': str(uuid.uuid4()),
                },
                uenv={
                    'file': 'uEnv.txt',
                    'load': board.loading.uenv,
                },
            )

            # Generate boot.scr
            Utils.shell.run(
                "mkimage -C none -A arm -T script -d {build}/boot/boot.cmd {build}/boot/boot.scr".format(
                    build=env.paths['build']),
                shell=True
            )

    @staticmethod
    def _generate_fit(board):
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
                    file = env.paths['build'] + '/usr/lib/olinuxino-overlays/{}/{}'.format(board.soc, overlay)
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
                env.paths['build'] + '/usr/lib/olinuxino/kernel.its',
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

    def setup(self):
        board = env.objects['board']

        self._generate_uboot_env(board)
        self._generate_boot_cmd(board)
        self._generate_fit(board)


import datetime
import os
import uuid

import olimage.environment as env

from olimage.core.parsers import (Board, Partitions)
from olimage.core.utils import Utils


class Boot(object):
    @staticmethod
    def __call__(board: Board, partitions: Partitions):

        # Install source list
        Utils.install([
            '/boot/boot.cmd',
            '/boot/uEnv.txt',
            '/usr/lib/olinuxino/kernel.its'
        ])
        Utils.install('/etc/kernel/postinst.d/uboot-fit', mode='755')
        Utils.template.install(env.paths['debootstrap'] + '/boot/uEnv.txt', configs=None)

        # The FIT image is always located in /boot directory.
        # If there is such defined partition retrieve it's number. Do the same for /
        parts = {
            'boot': 1,
            'root': 1
        }
        for i in range(len(partitions)):
            partition = partitions[i]
            if partition.fstab.mount == '/':
                parts['root'] = i + 1
            elif partition.fstab.mount == '/boot':
                parts['boot'] = i + 1

        # Generate template
        Utils.template.install(
            env.paths['debootstrap'] + '/boot/boot.cmd',
            bootargs={
                'console': 'ttyS0,115200',
                'panic': 10,
                'loglevel': 4,
            },
            fit={
                'file': 'kernel.itb',
                'load': '0x60000000'
            },
            partitions=parts
        )

        # Generate boot.scr
        Utils.shell.run(
            "mkimage -C none -A arm -T script -d {rootfs}/boot/boot.cmd {rootfs}/boot/boot.scr".format(rootfs=env.paths['debootstrap']),
            shell=True
        )

        # Generate fdts and overlay data
        fdts = []
        overlays = []
        for variant in board.variants:
            if variant.fdt not in fdts:
                fdts.append(variant.fdt)

            for overlay in variant.overlays:
                file = env.paths['debootstrap'] + '/usr/lib/olimex-sunxi-overlays/{}/{}'.format(board.family, overlay)
                if overlay not in overlays and os.path.exists(file):
                    overlays.append(overlay)

        # Remap board fdt and overlays
        variants = []
        for variant in board.variants:
            dtbo = []
            for overlay in variant.overlays:
                if overlay in overlays:
                    dtbo.append(overlays.index(overlay) + 1)

            variants.append({
                'name': str(variant),
                'fdt': fdts.index(variant.fdt) + 1,
                'id': variant.id,
                'overlays': dtbo,
                'compatible': 'olimex,{}'.format(str(variant).lower())
            })

        # Generate load addresses for fdt files
        temp = []
        for fdt in fdts:
            temp.append({fdt: {'load': '0x4FA00000'}})
        fdts = temp

        # Generate load addresses for overlays
        addr = 0x4FA10000
        temp = []
        for overlay in overlays:
            temp.append({overlay: {'load': '0x{:08X}'.format(addr)}})
            addr += 0x10000
        overlays = temp

        Utils.template.install(
            env.paths['debootstrap'] + '/usr/lib/olinuxino/kernel.its',
            board=board,
            fdts=fdts,
            kernel={
                'load': '0x40080000',
                'entry': '0x40080000'
            },
            overlays=overlays,
            ramdisk={
                'load': '0x4FE00000',
                'entry': '0x4FE00000'
            },
            stamp={
                'date': str(datetime.datetime.now()),
                'uuid': str(uuid.uuid4()),
            },
            variants=variants,

        )

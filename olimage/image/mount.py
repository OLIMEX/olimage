import os
import re
import shutil
import time

import olimage.environment as env

from olimage.core.parsers import (Board, Boards)
from olimage.core.parsers.partitions import Partition
from olimage.core.utils import Utils


class Map(object):
    def __init__(self, image, partitions):

        self._board: Board = Boards().get_board(env.options['board'])
        self._image = image
        self._partitions = partitions

        # Store partition -> mapped device dictionary
        self._devices = {}

    def __enter__(self):
        lines = Utils.shell.run('kpartx -avs {}'.format(self._image)).decode('utf-8', 'ignore')
        for line in lines.splitlines():
            w = line.split()
            if w[0] == 'add':
                device = os.path.join('/dev/mapper', w[2])
                index = int(re.match(r'^loop\d+p(\d+)$', w[2])[1])

                if self._board.soc == "stm32mp1xx":
                    self._devices["root"] = {
                            'device': device,
                        }
                else:
                    # Get partition and set device
                    partition: Partition
                    partition = self._partitions[index - 1]
                    self._devices[str(partition)] = {
                            'device': device,
                        }

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        Utils.shell.run('kpartx -dvs {}'.format(self._image))

    def device(self, partition):
        if isinstance(partition, Partition):
            partition = str(partition)

        try:
            return self._devices[partition]['device']
        except KeyError:
            raise Exception("Partition \'{}\' in not mapped!".format(partition))

    def uuid(self, partition):
        if isinstance(partition, Partition):
            partition = str(partition)

        try:
            return self._devices[partition]['uuid']
        except KeyError:
            raise Exception("Partition \'{}\' in not mapped!".format(partition))


class Mount(Map):

    def __enter__(self):
        super().__enter__()

        for partition in self._partitions:
            device = self._devices[str(partition)]['device']
            uuid = Utils.shell.run('blkid -s UUID -o value {}'.format(device)).decode().splitlines()[0]
            mount = Utils.shell.run('mktemp -d').decode().strip()

            self._devices[str(partition)]['mount'] = mount
            self._devices[str(partition)]['uuid'] = uuid

            self._mount(self._devices[str(partition)])

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        for partition in self._partitions:
            self._umount(self._devices[str(partition)])

        super().__exit__(exc_type, exc_val, exc_tb)

    def _mount(self, device: dict):
        if os.path.exists(device['mount']):
            shutil.rmtree(device['mount'])
        os.mkdir(device['mount'])

        Utils.shell.run('mount {} {}'.format(device['device'], device['mount']))

    def _umount(self, partition: dict):
        while True:
            try:
                Utils.shell.run('umount {}'.format(partition['mount']))
                break
            except OSError:
                time.sleep(1)

        shutil.rmtree(partition['mount'])

    def mountpoint(self, partition):
        if isinstance(partition, Partition):
            partition = str(partition)

        try:
            return self._devices[partition]['mount']
        except KeyError:
            raise Exception("Partition \'{}\' in not mounted!".format(partition))


class Mounter(object):
    map = Map
    mount = Mount

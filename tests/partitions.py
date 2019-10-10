import unittest
import yaml

import dependecy_injector

from olimage.rootfs.partition import Partitions


class MyTestCase(unittest.TestCase):
    def setUp(self):
        with open("olimage/configs/partitions.yaml", 'r') as f:
            self._data = yaml.full_load(f.read())

    def test_something(self):
        for part in Partitions(self._data['partitions']):
            part.gggg = 132
            # print(part.type)
            print(part.gggg)
            print(part.fstab)
            print(part.fstab.type)
            print(part.parted)
            print(part.parted.type)
            # print(part.rrt.fff

        # a = []
        # print(a)
        # a += p
        # print(a)
        # print(self._data)
        # self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()

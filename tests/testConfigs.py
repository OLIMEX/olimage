import os
import pinject
import shutil
import unittest

import olimage.rootfs.setup.setup as setup
import olimage.environment as env


class Configs(unittest.TestCase):
    def setUp(self) -> None:
        env.obj_graph = pinject.new_object_graph()

    def testHostname(self) -> None:
        setup.Setup.hostname("asdad", "aaaa")



if __name__ == '__main__':
    unittest.main()

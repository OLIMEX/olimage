import os
import pinject
import shutil
import unittest

import olimage.core.utils as utils
import olimage.environment as env


class Archive(unittest.TestCase):
    def setUp(self) -> None:
        env.obj_graph = pinject.new_object_graph()

        self.path = os.path.dirname(os.path.abspath(__file__)) + "/download"
        self.url = 'https://github.com/OLIMEX/olinuxino-overlays.git'

        # Create test directory
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
        os.mkdir(self.path)

    def tearDown(self) -> None:
        # Remove output directory after tests
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

    def test_clone(self):
        self.assertEqual(utils.Utils.download.git(self.url, self.path), self.path + '/master')

    def test_ref(self):
        ref = 'linux-5.1'
        self.assertEqual(utils.Utils.download.git(self.url, self.path, ref), self.path + '/' + ref)


if __name__ == '__main__':
    unittest.main()

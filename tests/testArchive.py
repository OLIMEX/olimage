import pinject
import unittest
import os

import olimage.core.utils as utils
import olimage.environment as env


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        env.obj_graph = pinject.new_object_graph()

    def test_archive(self):
        self.assertEqual('/olimage/olimage.tar.gz', utils.Utils.archive.gzip('/olimage/olimage'))
        os.remove('/olimage/olimage.tar.gz')

        self.assertEqual('/olimage/olimage.tar.bz2', utils.Utils.archive.bzip2('/olimage/olimage'))
        os.remove('/olimage/olimage.tar.bz2')

        self.assertEqual('/olimage/olimage.tar.xz', utils.Utils.archive.lzma('/olimage/olimage'))
        os.remove('/olimage/olimage.tar.xz')

    def test_extract(self):
        self.assertEqual('/olimage/olimage.tar.gz', utils.Utils.archive.gzip('/olimage/olimage'))

        utils.Utils.archive.extract('/olimage/olimage.tar.gz', '/olimage/tmp')

if __name__ == '__main__':
    unittest.main()

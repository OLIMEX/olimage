import os
import pinject
import shutil
import unittest

import olimage.core.utils as utils
import olimage.environment as env


class Archive(unittest.TestCase):
    def setUp(self) -> None:
        env.obj_graph = pinject.new_object_graph()

    def test_gzip(self):
        self.assertEqual('/olimage/olimage.tar.gz', utils.Utils.archive.gzip('/olimage/olimage'))
        os.remove('/olimage/olimage.tar.gz')

    def test_bzip2(self):
        self.assertEqual('/olimage/olimage.tar.bz2', utils.Utils.archive.bzip2('/olimage/olimage'))
        os.remove('/olimage/olimage.tar.bz2')

    def test_lzma(self):
        self.assertEqual('/olimage/olimage.tar.xz', utils.Utils.archive.lzma('/olimage/olimage'))
        os.remove('/olimage/olimage.tar.xz')

    def test_extract(self):
        self.assertEqual('/olimage/olimage.tar.gz', utils.Utils.archive.gzip('/olimage/olimage'))

        utils.Utils.archive.extract('/olimage/olimage.tar.gz', '/olimage/tmp')
        os.remove('/olimage/olimage.tar.gz')

        self.assertTrue(os.path.exists('/olimage/tmp/olimage'))
        shutil.rmtree('/olimage/tmp')

if __name__ == '__main__':
    unittest.main()

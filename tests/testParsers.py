import pinject
import unittest

import olimage.environment as env


class Configs(unittest.TestCase):
    def setUp(self) -> None:
        env.obj_graph = pinject.new_object_graph()

    def testRepositories(self) -> None:
        pass




if __name__ == '__main__':
    unittest.main()

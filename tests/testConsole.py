import unittest
import time

from olimage.core.io import Console


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._console = Console()

    def test_something(self):
        self._console.info("Printing with info()")

        with Console("Context manager level 0"):
            time.sleep(1.5)
            with Console("Context manager level 1"):
                time.sleep(1.5)
                with Console("Context manager level 2"):
                    time.sleep(1.5)
            with Console("Context manager level 1"):
                time.sleep(1.5)
            with Console("Context manager level 1"):
                time.sleep(1.5)
            with Console("Context manager level 1"):
                with Console("Context manager level 2"):
                    time.sleep(1.5)
                with Console("Context manager level 2"):
                    time.sleep(1.5)

        # self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()

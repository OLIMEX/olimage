import unittest

from olimage.core.parsers import ParserPackages


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._parser = ParserPackages()

    def load_packages(self, file):
        installed = []
        with open(file, 'r') as f:
            for line in f.readlines():
                words = line.split()
                if words[0] != 'ii':
                    continue

                installed.append(words[1])
        return installed

    def test_minimal(self):
        minimal = self._parser.get_variant('minimal').packages
        installed = self.load_packages('../docs/versions/debootstrap.txt')

        common = set(minimal) & set(installed)
        if common:
            print("Common packages between debootstrap and minimal")
            print(list(common))
        self.assertFalse(bool(common))

    def test_lite(self):
        minimal = self._parser.get_variant('lite').packages
        installed = self.load_packages('../docs/versions/minimal.txt')

        common = set(minimal) & set(installed)
        if common:
            print("Common packages between minimal and lite")
            print(list(common))
        self.assertFalse(bool(common))

    def test_base(self):
        minimal = self._parser.get_variant('base').packages
        installed = self.load_packages('../docs/versions/lite.txt')

        common = set(minimal) & set(installed)
        if common:
            print("Common packages between lite and base")
            print(list(common))
        self.assertFalse(bool(common))

    def test_full(self):
        minimal = self._parser.get_variant('full').packages
        installed = self.load_packages('../docs/versions/base.txt')

        common = set(minimal) & set(installed)
        if common:
            print("Common packages between base and full")
            print(list(common))
        self.assertFalse(bool(common))


if __name__ == '__main__':
    unittest.main()

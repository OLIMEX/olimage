import unittest

import cerberus
import yaml


class Parsers(unittest.TestCase):
    def testRepositories(self) -> None:
        with open('../configs/repositories.yaml', 'r') as f:
            data = yaml.full_load(f.read())

        with open("../olimage/core/parsers/schemas/repositories.yaml") as f:
            schema = yaml.full_load(f.read())

        v = cerberus.Validator()
        try:
            self.assertTrue(v.validate(data, schema))
        except AssertionError as e:
            print(v.errors)
            raise e


if __name__ == '__main__':
    unittest.main()

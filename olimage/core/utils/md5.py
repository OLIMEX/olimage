import logging
import os
import hashlib

import olimage.environment as env

from .shell import Shell

logger = logging.getLogger(__name__)


class Md5(object):
    @staticmethod
    def __call__(source=None, destination=None):
        hash_md5 = hashlib.md5()
        with open(source, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)

        with open(destination, 'w') as f:
            f.write("{}  {}\n".format(hash_md5.hexdigest(), os.path.basename(source)))

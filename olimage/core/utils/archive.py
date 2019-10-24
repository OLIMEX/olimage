import logging
import os
import tarfile

logger = logging.getLogger(__name__)


class Archive(object):
    @staticmethod
    def _tar(mode, input, output=None):
        basename = os.path.basename(input)
        path = os.path.dirname(input)

        if output is None:
            output = os.path.join(path, basename + '.tar.' + mode.split(':')[1])

        logger.info("Archiving {} to {}".format(input, output))
        with tarfile.open(name=output, mode=mode) as tar:
            tar.add(input, basename)

    @staticmethod
    def gzip(input, output=None):
        Archive._tar('w:gz', input, output)

    @staticmethod
    def bzip2(input, output=None):
        Archive._tar('w:bz2', input, output)

    @staticmethod
    def lzma(input, output=None):
        Archive._tar('w:xz', input, output)
import logging
import os
import tarfile

logger = logging.getLogger(__name__)


class Archive(object):
    """
    Archive/Extract files

    Supported formats are gzip, bzip2 and lzma
    """
    @staticmethod
    def _tar(mode, input, output=None):
        """
        Preform the actual compression

        :param mode: archive mode
        :param input: input file/directory
        :param output: output file
        :return: output file path
        """
        basename = os.path.basename(input)
        path = os.path.dirname(input)

        if output is None:
            output = os.path.join(path, basename + '.tar.' + mode.split(':')[1])

        logger.info("Archiving {} to {}".format(input, output))
        with tarfile.open(name=output, mode=mode) as tar:
            tar.add(input, basename)

        return output

    @staticmethod
    def gzip(input, output=None) -> str:
        """
        Perform gzip compression

        :param input: file or directory to be archived
        :param output: output file
        :return: output file path
        """
        return Archive._tar('w:gz', input, output)

    @staticmethod
    def bzip2(input, output=None) -> str:
        """
        Perform bzip2 compression

        :param input: file or directory to be archived
        :param output: output file
        :return: output file path
        """
        return Archive._tar('w:bz2', input, output)

    @staticmethod
    def lzma(input, output=None) -> str:
        """
        Perform lzma compression

        :param input: file or directory to be archived
        :param output: output file
        :return: output file path
        """
        return Archive._tar('w:xz', input, output)

    @staticmethod
    def extract(input: str, output) -> None:
        """
        Extract file

        :param input: compressed file
        :param output: output patch
        :return: None
        """
        logger.info("Extracting {} to {}".format(input, output))
        with tarfile.open(name=input, mode='r:{}'.format(input.split('.')[-1])) as tar:
            tar.extractall(path=output)


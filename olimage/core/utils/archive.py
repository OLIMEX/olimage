import logging
import os

from .shell import Shell

logger = logging.getLogger()


class Archive(object):
    """
    Archive/Extract files

    Supported formats are gzip, bzip2 and lzma
    """
    modes = {
        'gz': 'gzip',
        'bz2': 'bzip2',
        'lzma': 'lzma'
    }

    @staticmethod
    def _tar(mode: str, source: str, output=None) -> str:
        """
        Preform the actual compression

        :param mode: archive mode
        :param source: input file/directory
        :param output: output file
        :return: output file path
        """
        basename = os.path.basename(source)
        path = os.path.dirname(source)

        if output is None:
            output = os.path.join(path, basename + '.tar.' + mode)

        logger.info("Archiving {} to {}".format(source, output))
        Shell.run('tar --{} -cf {} -C {} .'.format(Archive.modes[mode], output, source))
        return output

    @staticmethod
    def gzip(source, output=None) -> str:
        """
        Perform gzip compression

        :param source: file or directory to be archived
        :param output: output file
        :return: output file path
        """
        return Archive._tar('gz', source, output)

    @staticmethod
    def bzip2(source, output=None) -> str:
        """
        Perform bzip2 compression

        :param source: file or directory to be archived
        :param output: output file
        :return: output file path
        """
        return Archive._tar('bz2', source, output)

    @staticmethod
    def lzma(source, output=None) -> str:
        """
        Perform lzma compression

        :param source: file or directory to be archived
        :param output: output file
        :return: output file path
        """
        return Archive._tar('lzma', source, output)

    @staticmethod
    def extract(source: str, output) -> None:
        """
        Extract file

        :param source: compressed file
        :param output: output patch
        :return: None
        """
        logger.info("Extracting {} to {}".format(source, output))
        Shell.run('tar -axf {} -C {}'.format(source, output))



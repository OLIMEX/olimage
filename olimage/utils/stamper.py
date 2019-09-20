import logging
import os

logger = logging.getLogger(__name__)


class Stamper(object):
    def __init__(self, path):
        self._path = path

    @property
    def stamps(self):
        """
        Check founded stamps

        :return: list with stamps
        """
        existing = []
        for stamp in self._stamps:
            file = os.path.join(self._path, '.stamp_{}'.format(stamp))
            if os.path.isfile(file):
                logger.debug("Found stamp: {}".format(file))
                existing += [stamp]

        return existing

    def stamp(self, name):
        if name not in self._stamps:
            raise ValueError("Invalid stamp name: .stamp_{}".format(name))

        file = os.path.join(self._path, '.stamp_{}'.format(name))
        logger.debug("Creating stamp: {}".format(file))

        open(file, 'x').close()

    def remove(self, name):
        if name not in self._stamps:
            raise ValueError("Invalid stamp name: .stamp_{}".format(name))

        file = os.path.join(self._path, '.stamp_{}'.format(name))
        logger.debug("Deleting stamp: {}".format(file))

        if os.path.exists(file):
            os.remove(file)

class RootFSStamper(Stamper):
    def __init__(self, path):
        super().__init__(path)
        self._stamps = [
            'debootstrap',  # qemu-debootstrap process finished successfully
            'configured',   # rootfs was configured
        ]

class PackageStamper(Stamper):
    def __init__(self, path):
        super().__init__(path)
        self._stamps = [
            'downloaded',   # Sources are downloaded
            'archived',     # Sources are archived
            'extracted',    # Sources are extracted to the build directory
            'configured',   # Sources are configured
        ]

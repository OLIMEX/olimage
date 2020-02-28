import os
import shutil

import olimage.environment as env
from olimage.core.io import Console
from olimage.core.parsers import Board
from olimage.core.parsers.packages import ParserPackages
from olimage.core.utils import Utils


class FileSystemBase(object):
    stages = []
    variant = None

    def __init__(self):
        """
        Initialize build directory and post-archive names
        """
        release = env.options['release']
        board: Board = env.objects['board']

        self._build_dir = os.path.join(env.paths['filesystem'], "{}-{}".format(release, self.variant))
        env.paths['build'] = self._build_dir

        parser = ParserPackages()
        self._variant_packages = parser.get_variant(self.variant)
        self._release_packages = parser.get_release(release)

    def __del__(self):
        Utils.shell.unbind(self._build_dir)

    @property
    def build_dir(self) -> str:
        """
        Get the current build directory

        :return: path to the current build directory
        """
        return self._build_dir

    def _install_packages(self) -> None:
        # Install packages
        with Console("Installing packages"):
            # Get release independent packages
            packages = self._variant_packages.packages

            # Append release specific packages
            if self._release_packages:
                packages += self._release_packages.get_variant(str(self._variant_packages))

            # Try 5 times to install packages
            count = 5
            _e = None

            while True:
                try:
                    Utils.shell.chroot('apt-get install -y {}'.format(' '.join(packages)), log_error=False)
                    break
                except Exception as e:
                    count -= 1
                    if count == 0:
                        _e = e
                        break

                    with Console("Retrying..."):
                        Utils.shell.chroot('apt-get clean')
                        Utils.shell.chroot('apt-get update')

            if _e:
                raise _e

    def cleanup(self):
        with Console("APT sources"):
            Utils.shell.chroot('apt-get clean')

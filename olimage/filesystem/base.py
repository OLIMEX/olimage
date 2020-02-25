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

    def _prepare_build_dir(self) -> None:
        """
        Remove previous build directory and create
        a new empty one

        :return: None
        """
        if os.path.exists(self._build_dir):
            shutil.rmtree(self._build_dir)

        os.mkdir(self._build_dir)

    def _install_packages(self) -> None:
        # Install packages
        with Console("Installing packages"):
            # Get release independent packages
            packages = self._variant_packages.packages

            # Append release specific packages
            if self._release_packages:
                packages += self._release_packages.get_variant(str(self._variant_packages))

            Utils.shell.chroot('apt-get update')
            Utils.shell.chroot('apt-get install -y {}'.format(' '.join(packages)), self._build_dir)

    def cleanup(self):
        with Console("APT sources"):
            Utils.shell.chroot('apt-get clean')

    def export(self):
        with Console("Creating archive: {}".format(os.path.basename(self._build_dir) + '.tar.gz')):
            Utils.archive.gzip(self._build_dir, exclude=['/dev/*', '/proc/*', '/run/*', '/tmp/*', '/sys/*'])
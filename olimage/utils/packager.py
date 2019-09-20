import logging
import os
import shutil

import yaml


from utils.printer import Printer
from utils.stamper import Stamper
from utils.package import Package


logger = logging.getLogger(__name__)


class Packager(Package):

    def __init__(self, name, path, config):

        # Initialize parent
        super().__init__(name, path, config)

        # Configure stamper
        self._stamper = Stamper(self._path['build'])

        # Search packager configuration
        dir = os.path.dirname(os.path.abspath(__file__))
        cfg = os.path.join(dir, '../configs/packager.yaml')

        if not os.path.exists(cfg):
            raise Exception("Configuration file \'{}\' doesn't exist".format(cfg))

        # Load config and search for name
        with open(cfg, 'r') as f:
            self._pkg = yaml.full_load(f.read())[name] # type: dict


    @property
    def printer(self):
        return self._printer

    @printer.setter
    def printer(self, printer):
        self._printer = printer

    def prepare(self, **kwargs):

        # Create directory and copy install files
        pkg_dir = os.path.join(self._path['build'], self._pkg['Package'])

        logger.info("Preparing build directory: {}".format(dir))
        if os.path.exists(pkg_dir):
            shutil.rmtree(pkg_dir)
        os.mkdir(pkg_dir)

        # Install target files
        size = 0
        for f in self._config['install']:
            src, dest = f.split(':')

            dest = os.path.join(pkg_dir, dest)

            if not os.path.exists(dest):
                os.makedirs(dest)

            logger.info("Copying {} to {}".format(src, dest))
            dest = os.path.join(dest, src)
            src = os.path.join(self._path['extract'], src)

            shutil.copyfile(src, dest)
            size += os.path.getsize(dest)

        # Generate control files
        debian = os.path.join(pkg_dir, 'DEBIAN')
        os.mkdir(debian)

        control = os.path.join(debian, 'control')
        logger.info("Generating control file: {}".format(control))

        # Populate some missing values
        self._pkg['Version'] = kwargs['version']
        self._pkg['Architecture'] = self._config['arch']
        self._pkg['Installed-Size'] = str(size // 1024)

        with open(control, 'w') as f:
            for key, value in self._pkg.items():

                f.write("{}: ".format(key))

                if value is not None:
                    # Replace \n with an actual new line
                    value = value.replace("\\n", '\n')
                    f.write(value)

                f.write('\n')







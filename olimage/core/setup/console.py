import olimage.environment as env

from olimage.core.io import Console
from olimage.core.utils import Utils

from .base import SetupAbstract


class SetupConsole(SetupAbstract):

    def setup(self, keymap: str, layout: str):

        # Configure console
        with Console("Generating console configuration"):
            Utils.shell.chroot(
                'bash -c \'\
                echo "console-setup console-setup/charmap47 select UTF-8" | debconf-set-selections -v; \
                echo "console-setup console-setup/codeset47 select Guess optimal character set\" | debconf-set-selections -v; \
                echo "console-setup console-setup/fontface47 select  Do not change the boot/kernel font" | debconf-set-selections -v\
                \''
            )

        # Configure keyboard
        with Console("Generating keyboard configuration: \'{}\'".format(keymap)):
            Utils.shell.chroot(
                'bash -c \'\
                echo "keyboard-configuration keyboard-configuration/altgr select The default for the keyboard layout" | debconf-set-selections -v; \
                echo "keyboard-configuration keyboard-configuration/model select Generic 105-key (Intl) PC" | debconf-set-selections -v; \
                echo "keyboard-configuration keyboard-configuration/xkb-keymap select {}" | debconf-set-selections -v; \
                echo "keyboard-configuration keyboard-configuration/compose	select No compose key" | debconf-set-selections -v; \
                echo "keyboard-configuration keyboard-configuration/ctrl_alt_bksp boolean true" | debconf-set-selections -v; \
                echo "keyboard-configuration keyboard-configuration/variant select {}" | debconf-set-selections -v\
                \''.format(keymap, layout)
            )

        # Install package
        with Console("Installing packages"):
            Utils.shell.chroot('apt-get install -y {}'.format(' '.join(self.packages)))

        # Run configuration
        with Console("Running setup"):
            Utils.install('/etc/default/console-setup')
            Utils.shell.chroot('setupcon --force --save-only -v')

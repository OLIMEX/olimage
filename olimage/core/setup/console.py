import olimage.environment as env

from olimage.core.utils import Utils
from olimage.core.io import Output


class Console(object):
    @staticmethod
    def __call__(path: str, keymap: str, layout: str):

        file = '/etc/default/console-setup'
        source = env.paths['overlay'] + file
        destination = path + file

        # Configure console
        with Output.substep("Generating console configuration"):
            Utils.shell.chroot(
                'bash -c \'\
                echo "console-setup console-setup/charmap47 select UTF-8" | debconf-set-selections -v; \
                echo "console-setup console-setup/codeset47 select Guess optimal character set\" | debconf-set-selections -v; \
                echo "console-setup console-setup/fontface47 select  Do not change the boot/kernel font" | debconf-set-selections -v\
                \'',
                path
            )

        # Configure keyboard
        with Output.substep("Generating keyboard configuration: \'{}\'".format(keymap)):
            Utils.shell.chroot(
                'bash -c \'\
                echo "keyboard-configuration keyboard-configuration/altgr select The default for the keyboard layout" | debconf-set-selections -v; \
                echo "keyboard-configuration keyboard-configuration/model select Generic 105-key (Intl) PC" | debconf-set-selections -v; \
                echo "keyboard-configuration keyboard-configuration/xkb-keymap select {}" | debconf-set-selections -v; \
                echo "keyboard-configuration keyboard-configuration/compose	select No compose key" | debconf-set-selections -v; \
                echo "keyboard-configuration keyboard-configuration/ctrl_alt_bksp boolean true" | debconf-set-selections -v; \
                echo "keyboard-configuration keyboard-configuration/variant select {}" | debconf-set-selections -v\
                \''.format(keymap, layout),
                path
            )

        # Install package
        with Output.substep("Installing packages"):
            Utils.shell.chroot(
                'apt-get install -y console-setup keyboard-configuration',
                path
            )

        # Install files
        Utils.shell.run('install -v -m 644 {} {}'.format(source, destination))

        # Run configuration
        with Output.substep("Running setup"):
            Utils.shell.chroot(
                'setupcon --force --save-only -v',
                path
            )

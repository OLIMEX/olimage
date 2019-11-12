from olimage.core.utils import Utils


class Console(object):
    @staticmethod
    def __call__(path: str, layout: str):

        # Configure console
        Utils.shell.chroot(
            'bash -c \'\
            echo "console-setup console-setup/charmap47 select UTF-8" | debconf-set-selections -v; \
            echo "console-setup console-setup/codeset47 select Guess optimal character set\" | debconf-set-selections -v; \
            echo "console-setup console-setup/fontface47 select  Do not change the boot/kernel font" | debconf-set-selections -v\
            \'',
            path
        )

        # Configure keyboard
        Utils.shell.chroot(
            'bash -c \'\
            echo "keyboard-configuration keyboard-configuration/altgr select The default for the keyboard layout" | debconf-set-selections -v; \
            echo "keyboard-configuration keyboard-configuration/model select Generic 105-key (Intl) PC" | debconf-set-selections -v; \
            echo "keyboard-configuration keyboard-configuration/xkb-keymap select {}" | debconf-set-selections -v; \
            echo "keyboard-configuration keyboard-configuration/compose	select No compose key" | debconf-set-selections -v; \
            echo "keyboard-configuration keyboard-configuration/ctrl_alt_bksp boolean true" | debconf-set-selections -v; \
            echo "keyboard-configuration keyboard-configuration/variant select {}" | debconf-set-selections -v\
            \''.format(layout, layout),
            path
        )

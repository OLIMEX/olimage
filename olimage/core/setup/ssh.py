from olimage.core.utils import Utils


class SSH(object):
    @staticmethod
    def __call__(path: str, ssh: bool):

        # Enable/disable service
        Utils.shell.chroot(
            'systemctl {} ssh'.format('enable' if ssh else 'disable'),
            path
        )

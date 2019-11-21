import cliapp
import logging
import shlex

import olimage.environment as env


class Shell(object):
    @staticmethod
    def run(command, logger=None, **kwargs):
        if logger is None or not isinstance(logger, logging.Logger):
            logger = logging.getLogger(__name__)

        def handle_output(data):
            for line in data.decode().rstrip().split('\n'):
                logger.debug(line)

        kw = dict()
        kw['env'] = env.env
        kw['stdout_callback'] = handle_output
        kw['stderr_callback'] = handle_output
        kw.update(kwargs)

        if 'shell' in kwargs and kwargs['shell']:
            command = [command]
        else:
            command = shlex.split(command)

        try:
            return cliapp.runcmd(command, **kw)
        except cliapp.app.AppException as e:
            msg: str = e.msg
            logger.error(msg)
            raise Exception(msg.splitlines()[0])

    @staticmethod
    def _bind(directory):
        Shell.run("mount -t proc proc {}/proc".format(directory))
        Shell.run("mount --bind /dev {}/dev".format(directory))
        Shell.run("mount --bind /dev/pts {}/dev/pts".format(directory))
        Shell.run("mount --bind /sys {}/sys".format(directory))

    @staticmethod
    def _unbind(directory):
        Shell.run("umount {}/sys".format(directory))
        Shell.run("umount {}/dev/pts".format(directory))
        Shell.run("umount {}/dev".format(directory))
        Shell.run("umount {}/proc".format(directory))

    @staticmethod
    def chroot(command, directory, logger=None, **kwargs):
        # TODO: User env.paths['debootstrap'] instead of directory
        Shell._bind(directory)
        try:
            Shell.run("chroot {} ".format(directory) + command, logger, **kwargs)
            Shell._unbind(directory)
        except Exception as e:
            Shell._unbind(directory)
            raise e

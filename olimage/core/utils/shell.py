import cliapp
import logging
import shlex

import olimage.environment as env

logger = logging.getLogger(__name__)
buffer = {
    'stdout': '',
    'stderr': '',
}

class Shell(object):
    @staticmethod
    def stderr_callback(data):
        for line in data.decode().rstrip().split('\n'):
            global buffer
            buffer['stderr'] += line + '\n'

            logger.debug(line)

    @staticmethod
    def stdout_callback(data):
        for line in data.decode().rstrip().split('\n'):
            global buffer
            buffer['stdout'] += line + '\n'

            logger.debug(line)

    @staticmethod
    def run(command, **kwargs):

        global buffer
        buffer['stdout'] = ''
        buffer['stderr'] = ''

        _e = None

        kw = dict()
        kw['env'] = env.env
        kw['stdout_callback'] = Shell.stdout_callback
        kw['stderr_callback'] = Shell.stderr_callback
        kw.update(kwargs)

        if 'shell' in kwargs and kwargs['shell']:
            command = [command]
        else:
            command = shlex.split(command)

        try:
            return cliapp.runcmd(command, **kw)
        except KeyboardInterrupt as e:
            _e = e
        except cliapp.app.AppException as e:
            msg: str = e.msg
            logger.error(msg)
            _e = Exception(msg.splitlines()[0] + '\n' + buffer['stderr'])

        if _e:
            raise _e

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
    def chroot(command, directory=None, **kwargs):
        # This should use env
        if directory is None:
            directory = env.paths['debootstrap']

        _e = None
        Shell._bind(directory)
        try:
            Shell.run("chroot {} ".format(directory) + command, **kwargs)
            Shell._unbind(directory)
        except KeyboardInterrupt:
            Shell._unbind(directory)
            _e = KeyboardInterrupt
        except Exception as e:
            Shell._unbind(directory)
            _e = e

        if _e:
            raise _e

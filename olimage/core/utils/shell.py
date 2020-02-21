import time

import cliapp
import logging
import shlex


import olimage.environment as env

logger = logging.getLogger()


class Shell(object):
    @staticmethod
    def run(command, **kwargs):

        def callback(data):
            for line in data.decode().rstrip().split('\n'):
                logger.debug(line)

        _e = None

        kw = dict()
        kw['env'] = env.env
        kw['stdout_callback'] = callback
        kw['stderr_callback'] = callback
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
            _e = Exception('\n'.join(msg.splitlines()))

        if _e:
            raise _e

    @staticmethod
    def _is_mounted(path):
        mounts = []
        with open('/proc/self/mountinfo', 'r') as f:
            for line in f.readlines():
                mounts.append(line.split()[4])

        return path in mounts

    @staticmethod
    def bind(path):
        if not Shell._is_mounted(path + '/proc'):
            Shell.run("mount -t proc proc {}/proc".format(path))
        if not Shell._is_mounted(path + '/dev'):
            Shell.run("mount --bind /dev {}/dev".format(path))
        if not Shell._is_mounted(path + '/dev/pts'):
            Shell.run("mount --bind /dev/pts {}/dev/pts".format(path))
        if not Shell._is_mounted(path + '/sys'):
            Shell.run("mount --bind /sys {}/sys".format(path))

    @staticmethod
    def unbind(path):
        for mount in ['/sys', '/dev/pts', '/dev', '/proc']:
            if Shell._is_mounted(path + mount):
                while True:
                    try:
                        Shell.run("umount {}".format(path + mount))
                    except OSError:
                        time.sleep(1)
                        continue
                    break

    @staticmethod
    def chroot(command, directory=None, **kwargs):
        # This should use env
        if directory is None:
            directory = env.paths['build']

        _e = None
        Shell.bind(directory)
        try:
            Shell.run("chroot {} ".format(directory) + command, **kwargs)
        except KeyboardInterrupt:
            _e = KeyboardInterrupt
        except Exception as e:
            _e = e

        if _e:
            # time.sleep(2)
            # Shell.unbind(directory)
            raise _e

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
    def _mountpoints():
        mounts = []
        with open('/proc/self/mountinfo', 'r') as f:
            for line in f.readlines():
                mounts.append(line.split()[4])
        return mounts

    @staticmethod
    def _bind(directory):
        m = Shell._mountpoints()
        if directory + '/proc' not in m:
            Shell.run("mount -t proc proc {}/proc".format(directory))
        if directory + '/dev' not in m:
            Shell.run("mount --bind /dev {}/dev".format(directory))
        if directory + '/dev/pts' not in m:
            Shell.run("mount --bind /dev/pts {}/dev/pts".format(directory))
        if directory + '/sys' not in m:
            Shell.run("mount --bind /sys {}/sys".format(directory))

    @staticmethod
    def _unbind(directory):
        m = Shell._mountpoints()
        if directory + '/sys' in m:
            Shell.run("umount {}/sys".format(directory))
        if directory + '/dev/pts' in m:
            Shell.run("umount {}/dev/pts".format(directory))
        if directory + '/dev' in m:
            Shell.run("umount {}/dev".format(directory))
        if directory + '/proc' in m:
            Shell.run("umount {}/proc".format(directory))

    @staticmethod
    def chroot(command, directory=None, **kwargs):
        # This should use env
        if directory is None:
            directory = env.paths['build']

        _e = None
        Shell._bind(directory)
        try:
            Shell.run("chroot {} ".format(directory) + command, **kwargs)
            Shell._unbind(directory)
        except KeyboardInterrupt:
            _e = KeyboardInterrupt
        except Exception as e:
            _e = e
        finally:
            time.sleep(0.1)
            Shell._unbind(directory)

        if _e:
            raise _e

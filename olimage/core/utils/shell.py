import time
import os

import cliapp
import logging
import shlex


import olimage.environment as env

logger = logging.getLogger()


class Shell(object):
    # mountpoints = ['/proc', '/dev', '/dev/pts', '/sys', '/run/dbus']
    mountpoints = ['/proc', '/dev', '/dev/pts', '/sys']

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
        for mount in Shell.mountpoints:
            if not Shell._is_mounted(path + mount):
                if not os.path.exists(path + mount):
                    os.makedirs(path + mount, 0o755, exist_ok=True)

                if mount == '/proc':
                    Shell.run("mount -t proc proc {}/proc".format(path))
                else:
                    Shell.run("mount --bind {} {}".format(mount, path + mount))

    @staticmethod
    def unbind(path):
        for mount in reversed(Shell.mountpoints):
            if Shell._is_mounted(path + mount):
                while True:
                    try:
                        Shell.run("umount {}".format(path + mount))
                    except OSError:
                        time.sleep(1)
                        continue
                    break

    @staticmethod
    def chroot(command, path=None, **kwargs):
        # This should use env
        if path is None:
            path = env.paths['build']

        _e = None
        Shell.bind(path)
        try:
            Shell.run("chroot {} ".format(path) + command, **kwargs)
        except KeyboardInterrupt:
            _e = KeyboardInterrupt
        except Exception as e:
            _e = e

        if _e:
            raise _e

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
    def chroot(command, directory, logger=None, **kwargs):
        Shell.run("chroot {} ".format(directory) + command, logger, **kwargs)
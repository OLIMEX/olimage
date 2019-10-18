import logging

import cliapp

import olimage.environment as env


class Worker(object):

    @staticmethod
    def run(command, logger=None, **kwargs):

        if not isinstance(command, list):
            raise ValueError("Command should be list")

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

        try:
            return cliapp.runcmd(command, **kw)
        except cliapp.app.AppException as e:
            msg: str = e.msg
            logger.error(msg)
            raise Exception(msg.splitlines()[0])

    @staticmethod
    def chroot(command, directory, logger=None, **kwargs):
        if not isinstance(command, list):
            raise ValueError("Command should be list")
        Worker.run(['chroot', directory] + command, logger, **kwargs)


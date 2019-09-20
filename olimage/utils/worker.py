import logging

import cliapp

import olimage.environment as environment


class Worker(object):

    @staticmethod
    def run(command, logger=None):

        if not isinstance(command, list):
            raise ValueError("Command should be list")

        if logger is None or not isinstance(logger, logging.Logger):
            logger = logging.getLogger(__name__)

        def handle_output(data):
            for line in data.decode().rstrip().split('\n'):
                logger.debug(line)

        kwargs = dict()

        kwargs['env'] = environment.env
        kwargs['stdout_callback'] = handle_output
        kwargs['stderr_callback'] = handle_output

        return cliapp.runcmd(command, **kwargs)

    @staticmethod
    def chroot(command, directory, logger=None):
        if not isinstance(command, list):
            raise ValueError("Command should be list")
        Worker.run(['chroot', directory] + command, logger)


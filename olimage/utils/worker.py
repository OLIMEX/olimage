import logging

import cliapp

import olimage.environment as environment


class Worker(object):
    def __init__(self):
        pass

    @staticmethod
    def run(*args):

        if isinstance(args[1], logging.Logger):
            logger = args[1]
        else:
            logger = logging.getLogger(__name__)

        def handle_output(data):
            for line in data.decode().rstrip().split('\n'):
                logger.debug(line)

        kwargs = dict()

        kwargs['env'] = environment.env
        kwargs['stdout_callback'] = handle_output
        kwargs['stderr_callback'] = handle_output

        return cliapp.runcmd(args[0], **kwargs)


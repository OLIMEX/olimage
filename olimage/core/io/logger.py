import logging


class Logger(logging.Logger):

    def print(self, msg):
        super().info(msg)

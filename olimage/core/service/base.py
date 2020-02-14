import abc

import colorama

from .exceptions import ServiceException


class ServiceBase(object):
    OPERATION_ENABLE = 0
    OPERATION_DISABLE = 1
    OPERATION_INSTALL = 2
    OPERATION_REMOVE = 3

    @staticmethod
    def get_operation_text(operation: int) -> str:
        if operation == ServiceBase.OPERATION_ENABLE:
            return "{}Enabling{}:".format(colorama.Fore.GREEN, colorama.Fore.RESET)
        elif operation == ServiceBase.OPERATION_DISABLE:
            return "{}Disabling{}:".format(colorama.Fore.RED, colorama.Fore.RESET)
        elif operation == ServiceBase.OPERATION_INSTALL:
            return "{}Installing{}:".format(colorama.Fore.YELLOW, colorama.Fore.RESET)
        elif operation == ServiceBase.OPERATION_DISABLE:
            return "{}Removing{}:".format(colorama.Fore.YELLOW, colorama.Fore.RESET)
        else:
            raise ServiceException("Unknown operation")

    @staticmethod
    @abc.abstractmethod
    def enable(*args, **kwargs):
        pass

    @staticmethod
    @abc.abstractmethod
    def disable(*args, **kwargs):
        pass

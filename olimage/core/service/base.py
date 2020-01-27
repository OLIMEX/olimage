import abc


class ServiceBase(object):
    @abc.abstractstaticmethod
    def name() -> str:
        pass

    @abc.abstractstaticmethod
    def enable():
        pass

    @abc.abstractstaticmethod
    def disable():
        pass
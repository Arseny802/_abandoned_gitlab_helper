from abc import ABCMeta, abstractmethod


class TBotApi:
    __metaclass__ = ABCMeta

    @abstractmethod
    def start(self, event, update):
        pass

    """Переместить объект"""

    @abstractmethod
    def stop(self, event, update):
        pass

    """Переместить объект"""

    @abstractmethod
    def help(self, event, update):
        pass

    """Переместить объект"""

    @abstractmethod
    def status(self, event, update):
        pass

    """Переместить объект"""

    @abstractmethod
    def ping(self, event, update):
        pass

    """Переместить объект"""

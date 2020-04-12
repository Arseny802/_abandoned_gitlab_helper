import logging
from os import path, mkdir

from common.model import LogLevels
from settings.configuration import Config


class LoggerInstance:
    logger = None

    __log_directory_name = 'logs/'

    __model_to_lib = {
        LogLevels.trace: logging.DEBUG,
        LogLevels.debug: logging.DEBUG,
        LogLevels.info: logging.INFO,
        LogLevels.warn: logging.WARNING,
        LogLevels.error: logging.ERROR,
        LogLevels.fatal: logging.FATAL,
    }

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LoggerInstance, cls).__new__(cls)
            cls.instance.initialize()
        return cls.instance

    def initialize(self):
        self.logger = logging.getLogger(Config.module_name)
        self.logger.setLevel(logging.DEBUG)

        fmt_str = '[%(asctime)s] [%(levelname)s] [%(threadName)s]: %(message)s'

        if not path.isdir(self.__log_directory_name):
            mkdir(self.__log_directory_name)
        logging.basicConfig(filename=self.__log_directory_name + Config.module_name + '.log',
                            level=self.__model_to_lib[Config.log_level], format=fmt_str)
        ch = logging.StreamHandler()
        ch.setLevel(self.__model_to_lib[Config.log_level])
        ch.setFormatter(logging.Formatter(fmt_str))
        self.logger.addHandler(ch)

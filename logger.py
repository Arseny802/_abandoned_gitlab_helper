import logging

from configuration import Config
from model import LogLevels


class LoggerInstance:
    logger = None

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

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(self.__model_to_lib[Config.log_level])

        # create formatter
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        self.logger.addHandler(ch)

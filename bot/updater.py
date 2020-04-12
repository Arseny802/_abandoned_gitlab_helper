import subprocess
from datetime import datetime

from common.logger import LoggerInstance
from settings.configuration import Config


class Updater:
    __logger = LoggerInstance().logger

    __last_day_update_got: int = 0

    def __init__(self):
        self.__config = Config()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Updater, cls).__new__(cls)
        return cls.instance

    def update(self):
        if not self.is_update_time():
            return
        self.__logger.info("Update started.")
        bash_command = "git pull"
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        self.__logger.info("Update finished. Result: {}".format(output))
        # FiXME: Add error output. Needs NoneType check.
        # if bool(error):
        #     self.__logger.error("Update got error: {}".format(error))

    def is_update_time(self):
        current_day = datetime.today().day
        if current_day == self.__last_day_update_got:
            return False
        # TODO: check update time interval (like 02AM - 05AM)
        return True

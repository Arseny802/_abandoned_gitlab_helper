import threading
import time
import traceback

from common.logger import LoggerInstance
from common.model import LogLevels
from settings.configuration import Config


class SingleJob(threading.Thread):
    __logger = LoggerInstance().logger
    running = False
    looping = False

    def __init__(self, name: str, function, looping: bool = False, delay: float = 1):
        super(SingleJob, self).__init__(target=self.__work)
        self.__config = Config()
        self.name = name
        self.looping = looping
        if delay > 1 and looping:
            self.delay = delay
        elif looping:
            self.delay = self.__config.default_job_delay_sec
        else:
            self.delay = 0
        self.function = function

    def begin(self):
        if not self.running:
            self.running = True
            self.start()

    def cancel(self):
        if self.running:
            self.running = False
            self.join()

    def __work(self):
        while self.looping and self.running:
            try:
                self.__logger.debug("Job '{}' started.".format(self.name))
                self.function()
                self.__logger.debug("Job '{}' finished.".format(self.name))
            except Exception as e:
                self.__logger.error("Job '{}': {}".format(self.name, e))
                if self.__config.log_level == LogLevels.debug:
                    traceback.print_exc()
            finally:
                # Do not wait if job will not restart
                if not self.looping or not self.running:
                    return
                self.__logger.debug("Sleeping {} seconds before job '{}' restart.".format(self.delay, self.name))
                time.sleep(self.delay)

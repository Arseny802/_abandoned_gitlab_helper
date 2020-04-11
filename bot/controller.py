import time
import traceback

from common.logger import LoggerInstance
from common.model import PipelineEventType, LogLevels
from git_lab.gitlab_client import GitlabClient
from job.job_poll import JobPull
from settings.configuration import Config
from tbot.telegram_client import TBot


class Controller:
    __logger = LoggerInstance().logger

    def __init__(self):
        self.__config = Config()
        self.__tgp = TBot()
        self.__gl_client = GitlabClient()
        self.__job_pull = JobPull()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Controller, cls).__new__(cls)
        return cls.instance

    def process(self):
        self.__logger.info("Controller process started")
        self.__job_pull.add_job_looping('check pipelines', self.check_pipelines, self.__config.check_gitlab_delay_sec)
        self.__job_pull.add_job_looping('telegram polling', self.__tgp.connect, self.__config.telegram_read_delay_sec)
        self.__job_pull.start_all_jobs()
        self.__logger.info("Controller process finished")

    def sleep(self):
        self.__logger.info("Controller sleeping started")
        time.sleep(self.__config.recheck_timeout_sec)
        self.__logger.info("Controller sleeping finished")

    def check_pipelines(self):
        self._send_events(self.__gl_client.check_projects())

    def _send_events(self, events):
        if events is None:
            return
        try:
            for event in events:
                event_text = "Pipeline for {} : {} has event. {}".format(event.project_name, event.ref, event.url)
                if event.event_type == PipelineEventType.FAILED:
                    event_text = "\U000026A0  Pipeline for {} : {} failed. {}".format(
                        event.project_name, event.ref, event.url)
                elif event.event_type == PipelineEventType.RESTORED:
                    event_text = "\U000026A0  Pipeline for {} : {} restored. {}".format(
                        event.project_name, event.ref, event.url)
                self.__tgp.push_message_to_chat(event.chat_id, event_text)
        except Exception as e:
            self.__logger.error("failed to find interesting events {}".format(e))
            if self.__config.log_level == LogLevels.debug:
                traceback.print_exc()

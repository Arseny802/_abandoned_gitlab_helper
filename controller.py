import time
import traceback

from telegram.ext import Updater, CommandHandler

from configuration import Config
from gitlab_client import GitlabClient
from logger import LoggerInstance
from model import PipelineEventType, LogLevels
from tgp import Tgp


class Controller:
    logger = LoggerInstance().logger
    config = None
    tgp = None
    gl_client = None
    jobs_cancelled = False

    __tgp_command_handlers = []

    def __init__(self):
        self.config = Config()
        self.tgp = Tgp()
        self.gl_client = GitlabClient()
        self.__tgp_command_handlers = [
            CommandHandler('help', self.tgp.help),
            CommandHandler('start', self.tgp.start),
            CommandHandler('stop', self.tgp.stop),
            CommandHandler('ping', self.tgp.ping),
            CommandHandler('ping', self.tgp.status),
        ]

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Controller, cls).__new__(cls)
        return cls.instance

    def process(self):
        self.start_job('check pipelines', self.config.check_gitlab_delay_sec, self.check_pipelines)
        try:
            self.logger.info('Connecting to telegram.')
            updater = Updater(self.config.telegram_token, use_context=True,
                              request_kwargs=self.config.get_proxy_settings())
            for command in self.__tgp_command_handlers:
                updater.dispatcher.add_handler(command)
            updater.job_queue.run_repeating(self.tgp.trottled_sending,
                                            interval=self.config.telegram_read_delay_sec, first=0)
            updater.start_polling()
            self.logger.info('Telegram bot polling')
            updater.idle()
            self.logger.info('Telegram bot idle')
        except Exception as e:
            self.jobs_cancelled = True
            self.logger.fatal("Telegram error {}".format(e))
            if self.config.log_level == LogLevels.debug:
                traceback.print_exc()

    def check_pipelines(self):
        self._send_events(self.gl_client.check_projects())

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
                self.tgp.push_message_to_chat(event.chat_id, event_text)
        except Exception as e:
            self.logger.error("failed to find interesting events {}".format(e))
            if self.config.log_level == LogLevels.debug:
                traceback.print_exc()

    # periodic job that checks pipelines
    def start_job(self, job_name, job_delay, job_function):
        while not self.jobs_cancelled:
            try:
                self.logger.debug("Job {} started.".format(job_name))
                job_function()
                self.logger.debug("Job {} finished.".format(job_name))
            except Exception as e:
                self.logger.error("job {}: {}".format(job_name, e))
                if self.config.log_level == LogLevels.debug:
                    traceback.print_exc()
            finally:
                self.logger.debug('Sleeping {} seconds before job {} restart.'.format(job_delay, job_name))
                time.sleep(job_delay)

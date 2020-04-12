import traceback
from queue import Queue

from telegram.ext import CommandHandler, Updater

from src.common import model
from src.common.logger import LoggerInstance
from src.settings.configuration import Config
from src.tbot.telegram_client_api import TBotApi


class TBot(TBotApi):
    logger = LoggerInstance().logger
    messages = None
    config = None

    running = False

    projects_state = {}
    chat_ids = []

    __help_message = """I know this commands:
    /help   - to see this message;
    /start  - to start conversation;
    /stop   - to stop our conversation;
    /ping   - to check if I'm not alive;
    /status - to get your git_lab status."""

    __command_handlers = []

    def __init__(self):
        self.config = Config()
        self.messages = Queue(self.config.message_queue_length)
        self.chat_ids = self.config.load_chat_ids()
        self.__command_handlers = [
            CommandHandler('help', self.help),
            CommandHandler('start', self.start),
            CommandHandler('stop', self.stop),
            CommandHandler('ping', self.ping),
            CommandHandler('ping', self.status),
        ]

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(TBot, cls).__new__(cls)
        return cls.instance

    def connect(self):
        if self.running:
            return
        try:
            self.logger.info('Connecting to telegram.')
            updater = Updater(self.config.telegram_token, use_context=True,
                              request_kwargs=self.config.get_proxy_settings())
            for command in self.__command_handlers:
                updater.dispatcher.add_handler(command)
            updater.job_queue.run_repeating(self.trottled_sending, interval=self.config.telegram_read_delay_sec,
                                            first=0)
            updater.start_polling(timeout=3)
            self.logger.info('Telegram bot polling')
            updater.idle()
            self.logger.info('Telegram bot idle')
        except Exception as e:
            self.running = False
            self.logger.fatal("Telegram error {}".format(e))
            if self.config.log_level == model.LogLevels.debug:
                traceback.print_exc()

    def start(self, event, update):
        self.logger.debug("Start command occurred; event: {}".format(event))
        self.register_chat(event.message.chat.id)

    def stop(self, event, update):
        self.logger.debug("Stop command occurred; event: {}".format(event))
        self.unregister_chat(event.message.chat.id)

    def help(self, event, update):
        self.logger.debug("Help command occurred; event: {}".format(event))
        self.push_message_to_chat(event.message.chat.id, self.__help_message)

    def status(self, event, update):
        self.logger.debug("Status command occurred; event: {}".format(event))
        self.push_message_to_chat(event.message.chat.id, "Status is.")

    def ping(self, event, update):
        self.logger.debug("Ping command occurred; event: {}".format(event))
        self.push_message_to_chat(event.message.chat_id, 'pong, {}!'.format(event.message.from_user.first_name))

    def register_chat(self, chat_id):
        if chat_id not in self.chat_ids:
            self.push_message_to_chat(chat_id, "saving your name...")
            self.chat_ids.append(chat_id)
            self.config.save_chat_ids(self.chat_ids)
            self.push_message_to_chat(chat_id, "OK, now I will notify you!")
        else:
            self.push_message_to_chat(chat_id, "I already know you.")

    def unregister_chat(self, chat_id):
        if chat_id in self.chat_ids:
            self.push_message_to_chat(chat_id, "forgetting your name...")
            self.chat_ids.remove(chat_id)
            self.config.save_chat_ids(self.chat_ids)
            self.push_message_to_chat(chat_id, "that's the last message I sent to you :(")
        else:
            self.push_message_to_chat(chat_id, "Sorry, I don't know you.")

    def push_message_to_chat(self, chat_id, text):
        self.logger.debug("Pushing {} to chat {}".format(text, chat_id))
        self.messages.put(model.Message(chat_id, text))

    def trottled_sending(self, context):
        if self.messages is None:
            self.logger.error("messages is None!")
        if self.messages.empty():
            self.logger.debug("Messages queue is empty.")
            return
        self.logger.info("Got {} messages in queue.".format(self.messages.qsize()))
        message = self.messages.get()
        if message is None:
            self.logger.warning("Got None message from queue.")
            return
        self.logger.debug("Sending message '{}' to chat with id {}.".format(message.text, message.chat_id))
        if message is context.bot.send_message(chat_id=message.chat_id, text=message.text):
            self.logger.debug("Couldn't send message to chat with id {}.".format(message.chat_id))
            self.messages.put(message)
        else:
            self.logger.debug("Message successfully sent to chat with id {}.".format(message.chat_id))


assert issubclass(TBot, TBotApi)

from common.model import LogLevels
from settings import persistence


class Config(object):
    module_name = 'gitlab_helper_bot'
    # TODO: dynamic URL usage by chat (use some default)
    # TODO: multi URL usage (few URLs per user)
    gitlab_address = 'https://gitlab.taxcom.ru'
    gitlab_token = None
    telegram_token = None
    message_queue_length = 1000
    log_level = LogLevels.debug

    recheck_timeout_sec = 1200
    default_job_delay_sec = 20
    telegram_read_delay_sec = 5
    check_gitlab_delay_sec = 60

    _projects_state = {}
    _chat_ids = []

    # TODO: merge configs, single config for each user
    _projects_state_fn = 'save_state/projects_state.json'
    _chat_ids_fn = 'save_state/chat_ids.json'

    persistence = persistence.Persistence()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            # TODO: create tbot token reading from console, storing a bit more secure
            with open('tokens/telegram_token', 'r') as token_file:
                cls.telegram_token = token_file.read()
            # TODO; make multi user registration, git_lab token reading from chat
            with open('tokens/gitlab_token', 'r') as token_file:
                cls.gitlab_token = token_file.read()
            persistence.Persistence.create_file(cls._projects_state_fn)
            persistence.Persistence.create_file(cls._chat_ids_fn)
            cls.instance = super(Config, cls).__new__(cls)
        return cls.instance

    @staticmethod
    def get_proxy_settings():
        # TODO: make dynamic proxy reading from set of sites
        return {
            'proxy_url': 'socks5://78.46.18.223:9050'
        }

    def load_project_state(self):
        if self._projects_state is {}:
            tmp = self.persistence.load(self._projects_state_fn)
            if tmp is not None:
                self._projects_state = tmp
        return self._projects_state

    def save_project_state(self, new_state: dict):
        self.persistence.save(new_state, self._chat_ids_fn)

    def load_chat_ids(self):
        if self._chat_ids is []:
            tmp = self.persistence.load(self._chat_ids_fn)
            if tmp is not None:
                self._chat_ids = tmp
        return self._chat_ids

    def save_chat_ids(self, chat_ids: list):
        self.persistence.save(chat_ids, self._chat_ids_fn)

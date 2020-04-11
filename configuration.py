import persistence
from model import LogLevels


class Config(object):
    module_name = 'TGP_helper_bot'
    gitlab_address = 'https://gitlab.taxcom.ru'
    gitlab_token = None
    telegram_token = None
    message_queue_length = 1000
    log_level = LogLevels.debug

    telegram_read_delay_sec = 5
    check_gitlab_delay_sec = 5

    _projects_state = {}
    _chat_ids = []

    _projects_state_fn = 'save_state/projects_state.json'
    _chat_ids_fn = 'save_state/chat_ids.json'

    persistence = persistence.Persistence()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            with open('tokens/telegram_token', 'r') as token_file:
                cls.telegram_token = token_file.read()
            with open('tokens/gitlab_token', 'r') as token_file:
                cls.gitlab_token = token_file.read()
            persistence.Persistence.create_file(cls._projects_state_fn)
            persistence.Persistence.create_file(cls._chat_ids_fn)
            cls.instance = super(Config, cls).__new__(cls)
        return cls.instance

    @staticmethod
    def get_proxy_settings():
        return {
            'proxy_url': 'socks5://94.102.52.28:1080'
        }

    def load_project_state(self):
        if self._projects_state is {}:
            tmp = self.persistence.load(self._projects_state_fn)
            if tmp is not None:
                self._projects_state = tmp
        return self._projects_state

    def save_project_state(self, new_state: {}):
        self.persistence.save(new_state, self._chat_ids_fn)

    def load_chat_ids(self):
        if self._chat_ids is []:
            tmp = self.persistence.load(self._chat_ids_fn)
            if tmp is not None:
                self._chat_ids = tmp
        return self._chat_ids

    def save_chat_ids(self, chat_ids: []):
        self.persistence.save(chat_ids, self._chat_ids_fn)

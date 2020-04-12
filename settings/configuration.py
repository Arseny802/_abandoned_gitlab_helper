from common.model import LogLevels
from settings import persistence


class Config(object):
    module_name: str = 'gitlab_helper_bot'
    # TODO: dynamic URL usage by chat (use some default)
    # TODO: multi URL usage (few URLs per user)
    gitlab_address: str = 'https://gitlab.taxcom.ru'
    gitlab_token: str = None
    telegram_token: str = None
    message_queue_length: int = 1000
    log_level: LogLevels = LogLevels.debug

    update_delay_sec: float = 3600  # an hour
    recheck_timeout_sec: float = 1200  # 20 minutes
    default_job_delay_sec: float = 20  # 20 seconds
    telegram_read_delay_sec: float = 5
    check_gitlab_delay_sec: float = 60

    _projects_state: dict = {}
    _chat_ids: list = []

    # TODO: merge configs, single config for each user
    _projects_state_fn: str = 'save_state/projects_state.json'
    _chat_ids_fn: str = 'save_state/chat_ids.json'

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
            tmp: list = self.persistence.load(self._chat_ids_fn)
            if tmp is not None:
                self._chat_ids = tmp
        return self._chat_ids

    def save_chat_ids(self, chat_ids: list):
        self.persistence.save(chat_ids, self._chat_ids_fn)

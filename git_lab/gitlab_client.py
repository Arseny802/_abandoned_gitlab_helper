import traceback

import gitlab

from common.logger import LoggerInstance
from common.model import ProjectState, PipelineState, PipelineEvent, PipelineEventType
from settings.configuration import Config


class GitlabClient:
    logger = LoggerInstance().logger
    config = Config()
    projects_state = {}
    gitlab_connection = None

    def check_projects(self):
        self.gitlab_connection = self.auth()
        if self.gitlab_connection is None:
            pass
        self.logger.debug('Checking projects...')
        new_projects_state = self._get_all_projects_states()
        events = self._find_interesting_events(self.projects_state, new_projects_state)
        if len(events) > 0:
            self.logger.info('Got events: {}'.format(events))
            return events
        self.logger.debug('Got no events.')
        self.config.save_project_state(new_projects_state)
        self.projects_state = new_projects_state
        return []

    def auth(self):
        gitlab_auth = None
        try:
            gitlab_auth = gitlab.Gitlab(Config.gitlab_address, private_token=self.config.gitlab_token)
            gitlab_auth.auth()
            self.logger.debug('Successfully auth to git_lab.')
        except Exception as e:
            self.logger.error('failed to connect to git_lab: {}'.format(e))
            traceback.print_exc()
        return gitlab_auth

    def _find_interesting_events(self, o_projects_state, n_projects_state):
        events = []
        try:
            for project_name, n_project_state in n_projects_state.items():
                o_project_state = o_projects_state.get(project_name)
                if o_project_state is None:
                    continue

                for ref, n_pipeline_state in n_project_state.pipeline_states.items():
                    o_pipeline_state = o_project_state.pipeline_states.get(ref)
                    if o_pipeline_state is None:
                        continue
                    old_pipeline_failed = o_pipeline_state.status == 'failed' or o_pipeline_state.status == 'canceled'
                    new_pipeline_failed = n_pipeline_state.status == 'failed' or n_pipeline_state.status == 'canceled'
                    new_pipeline = o_pipeline_state.id != n_pipeline_state.id

                    if (not old_pipeline_failed or new_pipeline) and new_pipeline_failed:
                        events.append(
                            PipelineEvent(11111, PipelineEventType.FAILED, project_name, ref, n_pipeline_state.url))
                    elif old_pipeline_failed and not new_pipeline_failed:
                        events.append(
                            PipelineEvent(11111, PipelineEventType.RESTORED, project_name, ref, n_pipeline_state.url))
        except Exception as e:
            self.logger.error("failed to find interesting events {}".format(e))
            traceback.print_exc()
        return events

    # building state for all projects and all pipelines we can put our hands on
    def _get_all_projects_states(self):
        self.logger.debug('Getting all projects states...')
        acc = {}

        for gl_project in self._get_user_projects():
            try:
                project_state = self._get_single_project_state(gl_project)
                acc[project_state.project_name] = project_state
            except Exception as e:
                self.logger.error("failed to get project state: {}".format(e))
                traceback.print_exc()
        self.logger.debug('Got all projects states.')
        return acc

    def _get_user_projects(self):
        self.logger.debug('Getting user projects...')
        current_user = self.gitlab_connection.users.get(self.gitlab_connection.user.id)
        user_projects = []
        for project in self.gitlab_connection.projects.list(all=True):
            if current_user in project.members.list(all=True):
                user_projects.append(project)
        self.logger.debug('Got user projects.')
        return user_projects

    def _get_single_project_state(self, gl_project):
        self.logger.debug("Getting single project state for {}".format(gl_project))
        project_name = gl_project.path_with_namespace
        pipeline_states = {}
        project_state = ProjectState(project_name, pipeline_states)
        gl_pipelines = gl_project.pipelines.list()

        for gl_pipeline in gl_pipelines:
            ref = gl_pipeline.ref
            # ignoring pipelines without ref and pipelines with pending statuses
            if ref is None or gl_pipeline.status in ['canceled', 'success', 'failed']:
                pass
            existing_pipeline_states = pipeline_states.get(ref)
            # saving only last pipeline for any given ref
            if existing_pipeline_states is None or existing_pipeline_states.id < gl_pipeline.id:
                pipeline_states[ref] = PipelineState(gl_pipeline.id, gl_pipeline.ref,
                                                     gl_pipeline.status, gl_pipeline.web_url)
        return project_state

from common.logger import LoggerInstance
from job import Job
from settings.configuration import Config


class JobPull:
    logger = LoggerInstance().logger
    config = None

    jobs = {}

    def __init__(self):
        self.config = Config()

    def add_job_onetime(self, name: str, function):
        job = Job(name, function, False)
        self.__add_job(job)

    def add_job_looping(self, name: str, function, delay: float):
        job = Job(name, function, True, delay)
        self.__add_job(job)

    def __add_job(self, job: Job):
        if self.contains_job(job.name):
            pass
        self.logger.info("Added job '{}' to pull.".format(job.name))
        item = {job.name: job}
        self.jobs.update(item)

    def remove_job(self, job_name: str):
        if self.contains_job(job_name):
            del self.jobs[job_name]
            self.logger.info("Removed job '{}' from pull.".format(job_name))

    def contains_job(self, job_name):
        return job_name in self.jobs.keys()

    def start_job(self, job_name: str):
        if self.contains_job(job_name):
            self.jobs[job_name].begin()
            self.logger.info("Job '{}' started in pull.".format(job_name))

    def stop_job(self, job_name: str):
        if self.contains_job(job_name):
            self.jobs[job_name].cancel()
            self.logger.info("Job '{}' stopped in pull.".format(job_name))

    def start_all_jobs(self):
        for job in self.jobs.values():
            self.start_job(job.name)

    def stop_all_jobs(self):
        for job in self.jobs.values():
            self.stop_job(job.name)

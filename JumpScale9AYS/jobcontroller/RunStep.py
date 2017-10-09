import asyncio
from js9 import j


class RunStep:
    """
    A run step is a portion of a run
    It consist of multiple jobs that can be execute concurently
    """
    def __init__(self, run, nr, dbobj):
        self.run = run
        self.dbobj = dbobj
        self.dbobj.number = nr
        self.logger = j.atyourservice.server.logger

    @property
    def state(self):
        return self.dbobj.state.__str__()

    @state.setter
    def state(self, state):
        self.dbobj.state = state

    @property
    def services(self):
        return [job.service for job in self.jobs]

    @property
    def jobs(self):
        res = []
        for obj in self.dbobj.jobs:
            job_model = j.core.jobcontroller.db.jobs.get(obj.key)
            if job_model:
                res.append(job_model.objectGet())
            else:
                self.logger.info('No job found with key [%s]' % obj.key)
        return res

    def _fake_exec(self, job):
        job.model.dbobj.state = 'ok'
        action_name = job.model.dbobj.actionName
        # if the action is a reccuring action, save last execution time in model
        if action_name in job.service.model.actionsRecurring:
            job.service.model.actionsRecurring[action_name].lastRun = j.data.time.epoch

        service_action_obj = job.service.model.actions[action_name]
        service_action_obj.state = 'ok'
        job.save()
        # return valid done future, same as if job finished properly
        future = asyncio.Future()
        future.set_result(None)
        return future

    async def execute(self):

        coros = []
        jobs = []
        for job in self.jobs:

            # don't re-execute succesfull jobs
            if job.model.state == 'ok':
                continue

            action_name = job.model.dbobj.actionName
            service = job.service
            action_timeout = service.model.actions[action_name].timeout
            if action_timeout == 0:
                action_timeout = 3000

            self.logger.info('execute %s' % job)

            if job.service.aysrepo.no_exec is True:
                # don't actually execute anything
                coros.append(self._fake_exec(job))
            else:
                coros.append(asyncio.wait_for(job.execute(), action_timeout))
            jobs.append(job)

        results = await asyncio.gather(*coros, return_exceptions=True)
        self.state = 'ok'
        for i, result in enumerate(results):
            job = jobs[i]
            if isinstance(result, Exception):
                self.logger.error("{} failed:\n{}".format(job, result))
                self.state = 'error'

        self.logger.info("runstep {}: {}".format(self.dbobj.number, self.state))

    def __repr__(self):
        out = "step:%s (%s)\n" % (self.dbobj.number, self.state)
        for job in self.jobs:
            out += "- %-25s %-25s ! %-15s (%s)\n" % \
                (job.model.dbobj.actorName, job.model.dbobj.serviceName, job.model.dbobj.actionName, job.model.dbobj.state)
        return out

    __str__ = __repr__

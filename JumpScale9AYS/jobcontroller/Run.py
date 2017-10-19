import colored_traceback
from .RunStep import RunStep
from js9 import j
import json
import aiohttp
colored_traceback.add_hook(always=True)
RETRY_DELAY = [10, 30, 60, 300, 600, 1800]  # time of each retry in seconds, total: 46min 10sec


class Run:

    def __init__(self, model):
        self.lastnr = 0
        self.logger = j.atyourservice.server.logger
        self.model = model

    @property
    def steps(self):
        steps = []
        for dbobj in self.model.dbobj.steps:
            step = RunStep(self, dbobj.number, dbobj=dbobj)
            steps.append(step)
        return steps

    @property
    def aysrepo(self):
        return j.atyourservice.server.aysRepos.get(path=self.model.dbobj.repo)

    @property
    def state(self):
        return self.model.dbobj.state

    @state.setter
    def state(self, state):
        self.model.dbobj.state = state

    @property
    def key(self):
        return self.model.key

    @property
    def timestamp(self):
        return self.model.epoch

    def delete(self):
        self.model.delete()

    def newStep(self):
        self.lastnr += 1
        dbobj = self.model.stepNew()
        step = RunStep(self, self.lastnr, dbobj=dbobj)
        return step

    @property
    def services(self):
        res = []
        for step in self.steps:
            res.extend(step.services)
        return res

    def hasServiceForAction(self, service, action):
        for step in self.steps:
            for job in step.jobs:
                if job.model.dbobj.actionName != action:
                    continue
                if job.service == service:
                    return True
        return False

    def get_retry_level(self):
        """
        find lowest error level
        """
        levels = set()
        for step in self.steps:
            for job in step.jobs:
                service_action_obj = job.service.model.actions[job.model.dbobj.actionName]
                if service_action_obj.errorNr > 0:
                    levels.add(service_action_obj.errorNr)
        if levels:
            return min(levels)

    def get_retry_info(self):
        runInfo = {}
        retry = self.get_retry_level()
        if retry and self.retries[0] != 0 and retry <= len(self.retries):
            # capnp list to python list
            remaining_retries = [x for x in self.retries]
            runInfo = {
                'retry-number': retry,
                'duration': self.retries[retry - 1],
                'remaining-retries': remaining_retries[retry:]
            }
        return runInfo

    @property
    def error(self):
        out = "%s\n" % self
        out += "***ERROR***\n\n"
        for step in self.steps:
            if step.state == "ERROR":
                for key, action in step.actions.items():
                    if action.state == "ERROR":
                        out += "STEP:%s, ACTION:%s" % (step.nr, step.action)
                        out += self.db.get_dedupe("source",
                                                  action.model["source"]).decode()
                        out += str(action.result or '')
        return out

    @property
    def callbackUrl(self):
        return self.model.dbobj.callbackUrl

    @callbackUrl.setter
    def callbackUrl(self, callbackUrl):
        self.model.dbobj.callbackUrl = callbackUrl

    @property
    def retries(self):
        if not self.model.dbobj.retries:
            # if dev mode will only use the first value of default config with default number of retries
            if j.atyourservice.server.dev_mode:
                self.model.dbobj.retries = [RETRY_DELAY[0]] * len(RETRY_DELAY)
            else:
                self.model.dbobj.retries = RETRY_DELAY
        return self.model.dbobj.retries

    @retries.setter
    def retries(self, retries):
        self.model.dbobj.retries = retries

    def reverse(self):
        ordered = []
        for i, _ in enumerate(self.model.dbobj.steps):
            orphan = self.model.dbobj.steps.disown(i)
            ordered.append(orphan)

        for i, step in enumerate(reversed(ordered)):
            self.model.dbobj.steps.adopt(i, step)
            self.model.dbobj.steps[i].number = i + 1

        self.model.save()

    def save(self):
        self.model.save()

    async def execute(self):
        """
        Execute executes all the steps contained in this run
        if a step finishes with an error state.
        print the error of all jobs in the step that has error states then raise any
        exeception to stop execution
        """
        self.state = 'running'
        self.save()
        try:
            for step in self.steps:

                await step.execute()

                if step.state == 'error':
                    self.logger.error("error during execution of step {} in run {}".format(step.dbobj.number, self.key))
                    self.state = 'error'
                    err_msg = ''
                    for job in step.jobs:
                        if job.model.state == 'error':
                            if len(job.model.dbobj.logs) > 0:
                                log = job.model.dbobj.logs[-1]
                                print(job.str_error(log.log))
                                err_msg = log.log

                    raise j.exceptions.RuntimeError(err_msg)

            self.state = 'ok'
        except:
            self.state = 'error'
            raise
        finally:
            self.save()
            if self.callbackUrl:
                runInfo = self.get_retry_info()
                data = {'runid': self.key, 'runState': self.state.__str__(), 'retries': runInfo}
                async with aiohttp.ClientSession() as session:
                    await session.post(self.callbackUrl, headers={'Content-type': 'application/json'}, data=json.dumps(data))

    def __repr__(self):
        out = "RUN:%s\n" % (self.key)
        out += "-------\n"
        for step in self.steps:
            out += "## step:%s\n\n" % step.dbobj.number
            out += "%s\n" % step
        return out

    __str__ = __repr__

    def __lt__(self, other):
        return self.model.dbobj.lastModDate < other.model.dbobj.lastModDate

    def __gt__(self, other):
        return self.model.dbobj.lastModDate > other.model.dbobj.lastModDate

    def __eq__(self, other):
        return self.model.key == other.model.key

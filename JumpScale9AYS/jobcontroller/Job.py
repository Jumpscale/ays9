from js9 import j
from .SourceLoader import SourceLoader
from JumpScale9.errorhandling.ErrorConditionObject import ErrorConditionObject
import colored_traceback
import pygments.lexers
import cProfile
from contextlib import contextmanager
import asyncio
import functools
import logging
import traceback
from collections import MutableMapping


colored_traceback.add_hook(always=True)


def _execute_cb(job, future):
    """
    callback call after a job has finished executing
    job: is the job object
    future: future that hold the result of the job execution
    """
    if job._cancelled is True:
        return

    service_action_obj = None

    if job.service is not None:
        action_name = job.model.dbobj.actionName
        if action_name in job.service.model.actions:
            service_action_obj = job.service.model.actions[action_name]
            service_action_obj.lastRun = j.data.time.epoch

    exception = None
    try:
        exception = future.exception()
    except asyncio.CancelledError as err:
        exception = err
        job.logger.info("{} has been cancelled".format(job))
    if exception is not None:
        job.state = 'error'
        job.model.dbobj.state = 'error'
        if service_action_obj:
            service_action_obj.state = 'error'
            service_action_obj.errorNr += 1
            job.service.model.dbobj.state = 'error'

        ex = exception if exception is not None else TimeoutError()

        eco = j.errorhandler.processPythonExceptionObject(ex)
        job._processError(eco)

        if exception:
            tb_lines = [line.rstrip('\n') for line in traceback.format_exception(exception.__class__, exception, exception.__traceback__)]
            job.logger.error('\n'.join(tb_lines))
    else:
        job.state = 'ok'
        job.model.dbobj.state = 'ok'
        if service_action_obj:
            service_action_obj.state = 'ok'
            service_action_obj.errorNr = 0
        if job.service:
            job.service.model.dbobj.state = 'ok'

        job.logger.info("job {} done sucessfuly".format(str(job)))

    if service_action_obj.period > 0:   # recurring action.
        job.model.save()
        job.model.delete()
        del job
    else:
        job.save()

@contextmanager
def generate_profile(job):
    """
    context manager that generate profile of the code it wrap
    """
    if job.model.dbobj.profile is False:
        yield
    else:
        try:
            pr = cProfile.Profile()
            pr.enable()
            yield
        finally:
            pr.create_stats()
            # TODO: *1 this is slow, needs to be fetched differently
            stat_file = j.sal.fs.getTempFileName()
            pr.dump_stats(stat_file)
            job.model.dbobj.profileData = j.sal.fs.fileGetBinaryContents(stat_file)
            j.sal.fs.remove(stat_file)


class JobHandler(logging.Handler):
    def __init__(self, job_model, level=logging.NOTSET):
        super().__init__(level=level)
        self._job_model = job_model

    def emit(self, record):
        if record.levelno <= 20:
            category = 'msg'
        elif 20 < record.levelno <= 30:
            category = 'alert'
        else:
            category = 'errormsg'
        self._job_model.log(msg=record.getMessage(), level=record.levelno, category=category, epoch=int(record.created), tags='')


class JobContext(MutableMapping):
    def __init__(self, model):
        self._dict = {}
        for ctx in model.dbobj.context:
            self._dict[ctx.key] = ctx.value

    def __getitem__(self, key):
        return self._dict.__getitem__(key)

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError("key can only be of type str")
        if not isinstance(value, str):
            raise TypeError("value can only be of type str")

        self._dict.__setitem__(key, value)

    def __delitem__(self, key):
        return self._dict.__delitem__(key)

    def __iter__(self):
        return self._dict.__iter__()

    def __len__(self):
        return self._dict.__len__()

    def __repr__(self):
        return self._dict.__repr__()

    def __str__(self):
        return self._dict.__str__()

    def keys(self):
        return self._dict.keys()


class Job:
    """
    is what needs to be done for 1 specific action for a service
    """

    def __init__(self, model):
        self.model = model
        self.context = JobContext(model)
        self._cancelled = False
        self._action = None
        self._service = None
        self._future = None
        self.saveService = True
        self._sourceLoader = None
        self.logger = j.logger.get('j.core.jobcontroller.job.{}'.format(self.model.key))
        self._logHandler = JobHandler(self.model)
        self.logger.addHandler(self._logHandler)

    def __del__(self):
        self.cleanup()

    @property
    def _loop(self):
        try:
            loop = asyncio.get_event_loop()
        except:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop

    def cleanup(self):
        """
        clean the logger handler from the job object so it doesn't make the job stays in memory
        """
        self.logger.removeHandler(self._logHandler)
        jc_log_refs = j.logger.logging.manager.loggerDict.get('j.core.jobcontroller', {})
        job_log_refs = j.logger.logging.manager.loggerDict.get('j.core.jobcontroller.job', {})

        # Properly cleaning logger referernces in logging module to avoid memory leaks.
        jc_log_refs.loggerMap.pop(self.logger, None)
        job_log_refs.loggerMap.pop(self.logger, None)
        j.logger.logging.manager.loggerDict.pop(self.logger.name, None)

        for h in self.logger.handlers:
            self.logger.removeHandler(h)
        self._logHandler = None
        self.logger = None

    @property
    def action(self):
        if self._action is None:
            self._action = j.core.jobcontroller.db.actions.get(self.model.dbobj.actionKey)
        return self._action

    def printLogs(self):
        logs = list()
        for log in self.model.dbobj.logs:
            logs.append(("{epoch} - {category}: {log}".format(
                epoch=j.data.time.epoch2HRDateTime(log.epoch),
                category=log.category,
                log=log.log
            )))
        logs = '\n'.join(logs)
        print(logs)
        return logs

    @property
    def sourceLoader(self):
        if self._sourceLoader is None:
            if self._service is None:
                raise j.exceptions.RuntimeError("can't dynamicly load action code, no service present in job object")
            self._sourceLoader = SourceLoader(self._service)
        return self._sourceLoader

    @property
    def method(self):
        return self.sourceLoader.get_method(self.model.dbobj.actionName)

    @property
    def service(self):
        if self._service is None:
            if self.model.dbobj.actorName != "":
                repo = j.atyourservice.server.aysRepos.get(path=self.model.dbobj.repoKey)
                try:
                    self._service = repo.serviceGetByKey(self.model.dbobj.serviceKey)
                except j.exceptions.NotFound:
                    # If run contains a delete, this is perfectly acceptable
                    self.logger.warning("job {} tried to access a non existing service {}.".format(self,self.model.dbobj.serviceKey))
                    return None
        return self._service

    @service.setter
    def service(self, value):
        self._service = value
        self.model.dbobj.serviceKey = value.model.key

    def _processError(self, eco):

        if j.data.types.string.check(eco):
            # case it comes from the result of the processmanager
            eco = j.data.serializer.json.loads(eco)

            epoch = eco['epoch']
            if eco['_traceback'] != '':
                category = 'trace'
                msg = eco['_traceback']
            elif eco['errormessage'] != '':
                category = 'errormsg'
                msg = eco['errormessage']
            else:
                raise j.exceptions.RuntimeError("error message empty, can't process error")

            level = int(eco['level'])
            tags = eco['tags']

        elif isinstance(eco, ErrorConditionObject):
            epoch = eco.epoch
            if eco._traceback != '':
                category = 'trace'
                msg = eco._traceback
            elif eco.errormessage != '':
                category = 'errormsg'
                msg = eco.errormessage
            else:
                raise j.exceptions.RuntimeError("error message empty, can't process error")

            level = eco.level
            tags = eco.tags

        self.model.log(
            msg=msg,
            level=level,
            category=category,
            epoch=epoch,
            tags=tags)

        self.save()

    def error(self, errormsg, level=1, tags=""):
        self.model.log(
            msg=errormsg,
            level=level,
            category="errormsg",
            tags=tags)
        self.save()
        raise RuntimeError(errormsg)

    def save(self):
        if self.saveService and self.service is not None:
            if self.model.dbobj.actionName in self.service.model.actions:
                service_action_obj = self.service.model.actions[self.model.dbobj.actionName]
                service_action_obj.state = str(self.model.dbobj.state)

            if not service_action_obj.longjob:
                self.service.saveAll()

        if not j.sal.fs.exists(j.sal.fs.joinPaths(self.service.aysrepo.path, "services")):
            return # repo destroyed or service is deleted.
        # fill the context list in capnp obj before save
        self.model.dbobj.init('context', len(self.context))
        i = 0
        for k, v in self.context.items():
            kv = self.model.dbobj.context[i]
            kv.key = k
            kv.value = v
            i += 1

        self.model.save()


    def executeInProcess(self):
        """
        deprecated, all jobs are exected in process now.
        it's now a synonyme of execute()
        """
        return self.execute()

    def execute(self):
        """
        this method returns a future
        you need to await it to schedule it the event loop.
        the future return a tuple containing (result, stdout, stderr)

        ex: result, stdout, stderr = await job.execute()
        """
        # for now use default ThreadPoolExecutor
        if self.model.dbobj.debug is False:
            self.model.dbobj.debug = self.sourceLoader.source.find('ipdb') != -1 or \
                                     self.sourceLoader.source.find('IPython') != -1
        if j.atyourservice.server.dev_mode or self.service.model.actions[self.action.dbobj.name].longjob is False:
            self._future = self._loop.run_in_executor(None, self.method, self)
        else:
            # THIS FEATURE IS VERY DANGEROUS: USE with CARE or you END UP with a blocked AYS.
            # CODE IN `inner` coroutine defined must be fully async or ays main thread will block.
            # typical definition:
            # def longjob(job):
            #     async def inner(job):
            #         ## code here
            #     return inner(job)
            # self.method here is longjob and u need to call it with job to get the coroutine object returned `inner`
            method = self.method(self)
            if not asyncio.iscoroutine(method):
                raise RuntimeError("the method used for a the long job %s of service %s is not a courotine" % (self.action.dbobj.name, self.service))

            self._future = self._loop.create_task(method)

        # register callback to deal with logs and state of the job after execution
        self._future.add_done_callback(functools.partial(_execute_cb, self))

        if self.service is not None and self.model.dbobj.actionName in self.service.model.actions:
            service_action_obj = self.service.model.actions[self.model.dbobj.actionName]
            service_action_obj.state = 'running'

        self.model.dbobj.state = 'running'

        self.save()
        return self._future

    def cancel(self):
        self._cancelled = True
        if self._future:
            self._future.remove_done_callback(_execute_cb)
            self._future.cancel()
            self.logger.info("job {} cancelled".format(self))

    def str_error(self, error):
        out = 'Error of %s:' % str(self)
        formatter = pygments.formatters.Terminal256Formatter(style=pygments.styles.get_style_by_name("vim"))

        if error.__str__() != "":
            out += "\n*TRACEBACK*********************************************************************************\n"

            lexer = pygments.lexers.get_lexer_by_name("pytb", stripall=True)
            tb_colored = pygments.highlight(error.__str__(), lexer, formatter)
            out += tb_colored

        out += "\n\n******************************************************************************************\n"
        return out

    def __repr__(self):
        out = "job: %s!%s (%s)" % (
            (self.model.dbobj.actorName, self.model.dbobj.serviceName, self.model.dbobj.actionName))
        return out

    __str__ = __repr__

from js9 import j

# from Worker import Worker
from collections import namedtuple

import inspect
# import msgpack
import time

from .models.ActionsCollection import ActionsCollection
from .models.RunsCollection import RunsCollection
from .models.JobsCollections import JobsCollection
from .Job import Job
from .Run import Run


from concurrent.futures import ThreadPoolExecutor

DBTuple = namedtuple('db', ['runs', 'jobs', 'actions'])


class JobController:
    """
    JobController is the interface on top of Jobs
    Allow you to put jobs on execution queues, get informations about jobs
    """

    def __init__(self):
        self.__jslocation__ = "j.core.jobcontroller"
        self.__imports__ = "pycapnp,msgpack-python"

        self.db = DBTuple(
            RunsCollection(),
            JobsCollection(),
            ActionsCollection(),
        )
        self._methods = {}
        self._executor = ThreadPoolExecutor()

        self._init = False

    def test(self):
        self.db.destroy()

        def test(msg, f="f", g=1):
            """
            cool test
            """
            print("hello")
            print(msg)
            return msg

        def test2(msg, f="f", g=1):
            """
            cool test2
            """
            return msg

        job = self.newJobFromMethod(test, msg="hallo2")
        res = job.executeInProcess()

        # PERFTEST BASIC (CAN DO ABOUT 1000 per sec, in process)
        def perftest():
            print("start perftest exec in process, will interprete code, create objects, ...")
            start = time.time()
            nr = 50
            for i in range(nr):
                job = self.newJobFromMethod(test2, msg="hallo%s" % i)
                job.model.save()
                res = job.executeInProcess()
            stop = time.time()
            print("nr of exec in process per sec:%s" % int(nr / (stop - start)))

        # j.tools.performancetrace.profile("perftest()", globals=locals())
        # perftest()

        # LETS NOW TEST a RUN which is a set of jobs

        def jobStepMethod(msg):
            print(msg)
            return msg

        run = self.newRun(simulate=True)
        for stepnr in range(5):
            step = run.newStep()
            for i in range(10):
                job = self.newJobFromMethod(jobStepMethod, msg="step:%s method:%s" % (stepnr, i))
                step.addJob(job)

        print(run)

    def newJobFromMethod(self, method, runKey="", **args):
        """
        method is link to method (function)
        """
        action = self.getActionObjFromMethod(method)
        if not j.core.jobcontroller.db.actions.exists(action.key):
            action.save()
        job = j.core.jobcontroller.db.jobs.new()
        job.dbobj.actionKey = action.key
        job.dbobj.actionName = action.dbobj.name
        job.dbobj.actorName = action.dbobj.actorName
        job.dbobj.runKey = runKey
        job.dbobj.state = "new"
        job.dbobj.lastModDate = j.data.time.getTimeEpoch()
        job.args = args

        job0 = Job(model=job)
        return job0

    def newJobFromActionKey(self, key, runKey="", **args):
        action = j.core.jobcontroller.db.action.get(key)
        job = j.core.jobcontroller.db.job.new()
        job.dbobj.actionKey = action.key
        job.dbobj.actionName = action.dbobj.name
        job.dbobj.actorName = action.dbobj.actorName
        job.dbobj.runKey = runKey
        job.dbobj.state = "new"
        job.dbobj.lastModDate = j.data.time.getTimeEpoch()
        job.args = args

        job0 = Job(model=job)
        return job0

    def newJobFromModel(self, model):
        job0 = Job(model=model)
        return job0

    def newRunFromModel(self, model):
        run0 = Run(model=model)
        return run0

    def newRun(self, repo, simulate=False):
        model = self.db.runs.new()
        run = Run(model=model)
        run.model.dbobj.lastModDate = j.data.time.getTimeEpoch()
        run.state = 'new'
        run.model.dbobj.repo = repo
        return run

    def getActionObjFromMethod(self, method):
        path = inspect.getsourcefile(method)
        src = j.data.text.strip(inspect.getsource(method))
        return self.getActionObjFromMethodCode(src, path)

    def getActionObjFromMethodCode(self, src, path="", actorName="", actionName=""):
        # leave this our own parsing, is much faster
        action = self.db.actions.new()
        action.dbobj.origin = path
        action.dbobj.name = actionName
        action.dbobj.actorName = actorName

        state = "D"
        comment = ""
        source = ""
        for line in src.split("\n"):
            if state == "D":
                name, args = j.data.text.parseDefLine(line, False)
                state = "M"
                continue
            if state == "M" and line[4:8] in ["'''", "\"\"\""]:
                state = "C"
                continue
            if state == "C":
                if line[4:8] in ["'''", "\"\"\""]:
                    state = "M"
                else:
                    comment += "%s\n" % line[4:]
                continue
            source += "%s\n" % line[4:]

        action.dbobj.name = name
        action.dbobj.doc = comment.rstrip() + "\n"
        action.code = source
        action.argsText = args

        return action

    def executeJobFromKey(self, jobkey):
        """
        """
        self.queue.put(jobguid)

    def getJobFromQueue(self, timeout=20):
        """
        @param queue: name of queue to listen on
        @type queue: string

        @param timeout: timeout in seconds
        @type timeout: int
        """
        raise NotImplementedError()
        guid = self.queue.get(timeout=timeout)
        return self.db.get(guid)

    def abortAllJobs(self):
        """
        will empty queue & abort all jobs
        abort means jobs will stay in db but state will be set
        """
        raise NotImplementedError()
        job = self.queue.get_nowait()
        while job is not None:
            job.state = "abort"
            job = self.queue.get_nowait()

    def removeAllJobs(self):
        """
        will empty queue & remove all jobs
        """
        raise NotImplementedError()
        job = self.queue.get_nowait()
        while job is not None:
            self.db.delete(job.dbobj.key)
            job = self.queue.get_nowait()

    def testPerformance(self):

        def test(msg, defa="sdsd", llist=[]):
            """
            cool test
            """
            print("hello")
            print(msg)
            return msg

        print("start perftest getsourcefile")
        start = time.time()
        nr = 60000
        for i in range(nr):
            inspect.getsourcefile(test)
        stop = time.time()
        print("nr of getsourcefile per sec:%s" % int(nr / (stop - start)))

        print("start perftest inspect.getargspec")
        start = time.time()
        nr = 30000
        for i in range(nr):
            inspect.getargspec(test)
        stop = time.time()
        print("nr of inspect.getargspec per sec:%s" % int(nr / (stop - start)))

        # print("start eval perftest")
        # start = time.time()
        # nr = 100000
        # for i in range(nr):
        #     eval("[1,2,3,4]")
        # stop = time.time()
        # print("nr of eval of list per sec:%s" % int(nr / (stop - start)))

        print("start perftest own parser of args")
        start = time.time()
        nr = 100000
        # r = "def something(me,also=   [],also2=[1],w=2,ee=\"sss\",wwww=  '33')"
        r = "def something(me, also=[],w=2)"
        for i in range(nr):
            j.data.text.parseDefLine(r)
        stop = time.time()
        print("nr of our own parser of args per sec:%s" % int(nr / (stop - start)))

        print("start perftest read sourcecode")
        start = time.time()
        nr = 5000
        for i in range(nr):
            path = inspect.getsourcefile(test)
            # inspect.getsource(test)
            src = j.data.text.strip(inspect.getsource(test))
        stop = time.time()
        print("nr of read sourcecode per sec:%s" % int(nr / (stop - start)))

        path = inspect.getsourcefile(test)
        src = j.data.text.strip(inspect.getsource(test))

        def perftest(src, path):
            print("start perftest creation of action objects")
            start = time.time()
            nr = 100000
            # r = "def something(me,also=   [],also2=[1],w=2,ee=\"sss\",wwww=  '33')"
            r = "def something(me, also=[],w=2)"
            for i in range(nr):
                self.getActionObjFromMethodCode(src, path)
                # self.getActionObjFromMethod(test)
            stop = time.time()
            print("nr of creation of actionobj per sec:%s" % int(nr / (stop - start)))

        # j.tools.performancetrace.profile("perftest(src,path)", globals=locals())  # {"perftest": perftest}
        # our own processing of code is fast, fetching the code is not, but was expected
        perftest(src, path)

        """
        DID SOME BENCHMARKING

        - msgpack of med complex args = 250k/sec
        - getsourcefile of a method: 100k/sec
        - getargspec: 40k/sec
        - getargspec: 200k/sec if own parser
        """

    # def startWorkers(self, nrworkers=8):
    #
    #     curdir = j.sal.fs.getDirName(inspect.getsourcefile(self.__init__))
    #
    #     self._workerPath = j.sal.fs.joinPaths(curdir, "Worker.py")
    #
    #     self.tmux = j.sal.tmux.createPanes4x4("workers", "actions", False)
    #
    #     paneNames = [pane.name for pane in self.tmux.panes]
    #     paneNames.sort()
    #     for i in range(nrworkers):
    #         name = paneNames[i]
    #         pane = self.tmux.getPane(name)
    #         cmd = "python3 %s -q worker%s" % (self._workerPath, i)
    #         pane.execute(cmd)

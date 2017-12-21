from js9 import j
import capnp
from JumpScale9AYS.jobcontroller.models.JobModel import JobModel
from JumpScale9AYS.jobcontroller.models import model_job_capnp as ModelCapnp
from JumpScale9Lib.data.capnp.ModelBase import ModelBaseCollection


class JobsCollection(ModelBaseCollection):
    """
    This class represent a collection of Jobs
    It's used to list/find/create new Instance of Job Model object
    """

    def __init__(self):
        self.logger = j.logger.get('j.core.jobcontroller.job-collection')
        self.namespace_prefix = 'jobs'
        category = 'Job'
        namespace = "%s:%s" % (self.namespace_prefix, category.lower())
        db = j.data.kvs.getRedisStore(namespace, namespace, **j.atyourservice.server.config['redis'])
        super().__init__(ModelCapnp.Job, category=category, namespace=namespace, modelBaseClass=JobModel, db=db, indexDb=db)

    def new(self):
        model = JobModel(
            key='',
            new=True,
            collection=self)
        return model

    def get(self, key):
        if not self.exists(key):
            return
        return JobModel(
            key=key,
            new=False,
            collection=self)

    def exists(self, key):
        return self._db.exists(key)

    def list(self, actor="", service="", action="", state="", serviceKey="", fromEpoch=0, toEpoch=9999999999999,
             tags=[], returnIndex=False):
        if actor == "":
            actor = ".*"
        if service == "":
            service = ".*"
        if action == "":
            action = ".*"
        if state == "":
            state = ".*"
        if serviceKey == "":
            serviceKey = ".*"
        epoch = ".*"
        regex = "%s:%s:%s:%s:%s:%s:*" % (actor, service, action, state, serviceKey, epoch)
        res0 = self._index.list(regex, returnIndex=True)
        res1 = []
        for index, key in res0:
            epoch = int(index.split(":")[-2])
            indexTags = index.split(":")[-1]
            tagsOK = True
            for tag in tags:
                if tagsOK and tag not in indexTags:
                    tagsOK = False
            if not tagsOK:
                continue
            if fromEpoch <= epoch and epoch < toEpoch:
                if returnIndex:
                    res1.append((index, key))
                else:
                    res1.append(key)
        return res1

    def find(self, actor="", service="", action="", state="", serviceKey="", fromEpoch=0, toEpoch=9999999999999, tags=[]):
        res = []
        for key in self.list(actor, service, action, state, serviceKey, fromEpoch, toEpoch, tags):
            if self.get(key):
                res.append(self.get(key))
        return res


    def getIndexFromKey(self, key):
        job = self.get(key)
        if job:
            tags = sorted(self.dbobj.tags, key=str.lower)
            ind = "%s:%s:%s:%s:%s:%s:%s" % (job.dbobj.actorName, job.dbobj.serviceName,
                                            job.dbobj.actionName, job.dbobj.state,
                                            job.dbobj.serviceKey, job.dbobj.lastModDate,
                                            ''.join(tags))
            return ind

    def delete(self, actor="", service="", action="", state="", serviceKey="", fromEpoch=0, toEpoch=9999999999999, tags=[]):
        '''
        Delete a job
        :param actor: actor name
        :param service: service name
        :param action: action name
        :param state: state of the job to be deleted
        :param serviceKey: key identifying the service
        :param fromEpoch: runs in this period will be deleted
        :param toEpoch: runs in this period will be deleted
        :param tags: jobs with these tags will be deleted
        '''
        for index, key in self.list(actor, service, action, state, serviceKey, fromEpoch, toEpoch, tags, True):
            self._index.index_remove(keys=index)
            self._db.delete(key=key)

    def destroy(self):
        self._db.destroy()
        self._index.destroy()

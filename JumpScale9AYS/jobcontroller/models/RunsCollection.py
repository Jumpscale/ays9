from js9 import j
import capnp
from JumpScale9AYS.jobcontroller.models.RunModel import RunModel
from JumpScale9AYS.jobcontroller.models import model_job_capnp as ModelCapnp
from JumpScale9Lib.data.capnp.ModelBase import ModelBaseCollection


class RunsCollection(ModelBaseCollection):
    """
    This class represent a collection of Runs
    It's used to list/find/create new Instance of Run Model object
    """

    def __init__(self):
        self.logger = j.logger.get('j.core.jobcontroller.run-collection')
        # connection to the key-value store index repository namespace
        category = "Run"
        self.namespace_prefix = 'runs'
        namespace = "%s:%s" % (self.namespace_prefix, category.lower())
        db = j.data.kvs.getRedisStore(namespace, namespace, **j.atyourservice.server.config['redis'])
        super().__init__(ModelCapnp.Run, category=category, namespace=namespace, modelBaseClass=RunModel, db=db, indexDb=db)

    def new(self):
        model = RunModel(
            key='',
            new=True,
            collection=self)
        return model

    def get(self, key):
        return RunModel(
            key=key,
            new=False,
            collection=self)

    def exists(self, key):
        return self._db.exists(key)

    def _list_keys(self, state="", fromEpoch=0, toEpoch=9999999999999, returnIndex=False):
        if state == "":
            state = ".*"
        epoch = ".*"
        regex = "%s:%s" % (state, epoch)
        res0 = self._index.list(regex, returnIndex=True)
        res1 = []
        for index, key in res0:
            epoch = int(index.split(":")[-1])
            if fromEpoch < epoch < toEpoch:
                if returnIndex:
                    res1.append((index, key))
                else:
                    res1.append(key)
        return res1

    def find(self, state="", repo="", fromEpoch=0, toEpoch=9999999999999):
        res = []
        for key in self._list_keys(state, fromEpoch, toEpoch):
            if self.exists(key):
                if self.get(key):
                    if repo:
                        model = self.get(key)
                        if model.dbobj.repo != repo:
                            continue
                    res.append(self.get(key))
        return res

    def delete(self, state="", repo="", fromEpoch=0, toEpoch=9999999999999):
        '''
        Delete a run
        :param state: state of the run to be deleted
        :param repo: repo path
        :param fromEpoch: runs in this period will be deleted
        :param toEpoch: runs in this period will be deleted
        '''
        for key in self._list_keys(state, fromEpoch, toEpoch):
            if repo:
                if self.exists(key):
                    model = self.get(key)

                    if model.dbobj.repo != repo:
                        continue
                    idx = str(model.dbobj.state) + ':' + str(model.dbobj.lastModDate)
                    self._index.index_remove(keys=idx)
                    # Remove jobs in the run

                    for step in model.dbobj.steps:
                        for job in step.jobs:
                            j.core.jobcontroller.db.jobs.delete(job.actorName, job.serviceName, job.actionName, step.state.__str__(), job.serviceKey)
                self._db.delete(key=key)

    def destroy(self):
        self._db.destroy()
        self._index.destroy()

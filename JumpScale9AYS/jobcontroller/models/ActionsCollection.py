from js9 import j
import capnp
from JumpScale9AYS.jobcontroller.models.ActionModel import ActionModel
from JumpScale9AYS.jobcontroller.models import model_job_capnp as ModelCapnp

ModelBaseCollection=j.data.capnp_tarantool.getModelBaseClassCollection

class ActionsCollection(ModelBaseCollection):
    """
    This class represent a collection of AYS Reposities
    It's used to list/find/create new Instance of Repository Model object
    """

    def __init__(self):
        self.logger = j.logger.get('j.core.jobcontroller.action-collection')
        # connection to the key-value store index repository namespace
        self.namespace_prefix = 'jobs'
        category = "Action"
        namespace = "%s:%s" % (self.namespace_prefix, category.lower())
        super().__init__(ModelCapnp.Action, category=category, namespace=namespace, modelBaseClass=ActionModel)

    def new(self):
        model = ActionModel(
            key='',
            new=True,
            collection=self)
        return model

    def get(self, key):
        return ActionModel(
            key=key,
            new=False,
            collection=self)

    def exists(self, key):
        return self._db.exists(key)

    def _list_keys(self, origin="", name="", returnIndex=False):
        if name == "":
            name = ".*"
        if origin == "":
            origin = ".*"
        regex = "%s:%s" % (origin, name)
        return self._index.list(regex, returnIndex=returnIndex)

    def find(self, origin="", name=""):
        res = []
        for key in self._list_keys(origin, name):
            res.append(self.get(key))
        return res

    def destroy(self):
        self._db.destroy()
        self._index.destroy()

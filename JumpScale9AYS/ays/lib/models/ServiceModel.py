from js9 import j
from JumpScale9AYS.ays.lib.models.ActorServiceBaseModel import ActorServiceBaseModel
from JumpScale9AYS.ays.lib.Service import Service
from JumpScale9AYS.ays.lib import model_capnp as ModelCapnp

VALID_STATES = ['new', 'installing', 'ok', 'error', 'disabled', 'changed']


class ServiceModel(ActorServiceBaseModel):

    def __init__(self, aysrepo, collection, key="", new=False):
        super().__init__(aysrepo=aysrepo, key=key, new=new, collection=collection)
        self._aysrepo = aysrepo
        self.logger = j.logger.get('j.atyourservice.server.service-model')

    @property
    def role(self):
        return self.dbobj.actorName.split(".")[0]

    @property
    def parent(self):
        if self.dbobj.parent.serviceName == '' or self.dbobj.parent.actorName == '':
            return None

        parents = self._aysrepo.db.services.find(name=self.dbobj.parent.serviceName, actor=self.dbobj.parent.actorName)
        if len(parents) <= 0:
            return None
        elif len(parents) > 1:
            raise j.exceptions.RuntimeError("More then one parent model found for model %s:%s :%s\n" % (
                self.dbobj.actorName, self.dbobj.name, parents))

        return parents[0]

    def index(self):
        # put indexes in db as specified
        if self.dbobj.parent.actorName != "":
            parent = "%s!%s" % (self.dbobj.parent.actorName, self.dbobj.parent.serviceName)
        else:
            parent = ""

        if len(self.dbobj.producers) == 0:
            ind = "%s:%s:%s:%s:%s" % (self.dbobj.name, self.dbobj.actorName, self.dbobj.state, parent, "")
            self.collection._index.index({ind: self.key})
        else:
            # now batch all producers as more than 1 index
            #@TODO: *1 test
            index = {}
            for producer in self.dbobj.producers:
                producer2 = "%s!%s" % (producer.actorName, producer.serviceName)
                ind = "%s:%s:%s:%s:%s" % (self.dbobj.name, self.dbobj.actorName, self.dbobj.state, parent, producer2)
                index[ind] = self.key
            self.collection._index.index(index)

    def delete(self):
        # delete actual model object
        if self.collection._db.exists(self.key):
            self.collection._db.delete(self.key)

        # delete in memory service object if it exists
        if self.key in self._aysrepo.db.services.services:
            del self._aysrepo.db.services.services[self.key]

    def objectGet(self, aysrepo):
        """
        returns an Service object created from this model
        """
        if self.key not in self._aysrepo.db.services.services:
            self._aysrepo.db.services.services[self.key] = Service.init_from_model(aysrepo=aysrepo, model=self)
        return self._aysrepo.db.services.services[self.key]

    def producerAdd(self, actorName, serviceName, key):
        """
        Add another service to the producers list
        """
        obj = self.collection.capnp_schema.ServicePointer.new_message(actorName=actorName,
                                                                      serviceName=serviceName,
                                                                      key=key)
        self.updateSubItem('producers', ['actorName', 'serviceName'], obj)

    def producerRemove(self, service):
        """
        Remove the service passed in argument from the producers list
        """
        for i, prod in enumerate(self.dbobj.producers):
            if prod.key == service.model.key:
                self.deleteSubItem('producers', i)

    def consumerAdd(self, actorName, serviceName, key):
        """
        Add another service to the consumers list
        """
        obj = self.collection.capnp_schema.ServicePointer.new_message(actorName=actorName,
                                                                      serviceName=serviceName,
                                                                      key=key)
        self.updateSubItem('consumers', ['actorName', 'serviceName'], obj)

    def consumerRemove(self, service):
        """
        Remove the service passed in argument from the producers list
        """
        for i, consumer in enumerate(self.dbobj.consumers):
            if consumer.key == service.model.key:
                self.deleteSubItem('consumers', i)

    def changeParent(self, new_parent):
        """
        Change the parent sevice to new_parent
        """
        service = self.objectGet(self._aysrepo)

        if service.parent == new_parent:
            return
        old_parent = '%s!%s' % (service.parent.model.dbobj.actorName, service.parent.name)
        old_parent_index = '{name}:{actor}:.*:{parent}:.*'.format(name=service.name, actor=self.dbobj.actorName,
                                                                  parent=old_parent)
        # remove old parent from the producers list.
        service.model.producerRemove(service.parent)
        # remove ourself from the consumers list of the old parent
        service.parent.model.consumerRemove(service)

        # relink to the new parent
        service.model.producerAdd(
            actorName=new_parent.model.dbobj.actorName,
            serviceName=new_parent.model.dbobj.name,
            key=new_parent.model.key)

        new_parent.model.consumerAdd(
            actorName=service.model.dbobj.actorName,
            serviceName=service.model.dbobj.name,
            key=service.model.key)

        service.model.dbobj.parent.actorName = new_parent.model.dbobj.actorName
        service.model.dbobj.parent.key = new_parent.model.key
        service.model.dbobj.parent.serviceName = new_parent.name

        # change path to new parent in the filesystem
        j.sal.fs.removeDirTree(service.path)
        skey = "%s!%s" % (service.model.role, service.model.dbobj.name)
        fullpath = j.sal.fs.joinPaths(new_parent.path, skey)
        newpath = j.sal.fs.pathRemoveDirPart(fullpath, service.aysrepo.path)
        service.model.dbobj.gitRepo.path = newpath
        service._path = ""

        # change service dataJSON to reflect the change in the parent
        actor = service.aysrepo.actorGet(service.model.dbobj.actorName)
        template = service.aysrepo.templateGet(actor.model.dbobj.name)
        argname = template.configDict['links']['parent']['argname']
        setattr(service.model.data, argname, new_parent.name)

        service.model.reSerialize()
        service.parent.model.reSerialize()
        new_parent.model.reSerialize()

        toRemoveItems = self.collection._db.list(old_parent_index, True)
        for (toRemove, key) in toRemoveItems:
            self.collection._db.dbindex.pop(toRemove)

        self.save()

# events

    def eventFilterSet(self, command, actions, channel="", tags="", secrets=""):
        self.logger.debug('set event filter on %s!%s' % (self.role, self.name))
        changed = False

        command = command.lower()
        channel = channel.lower()
        # action = actions.lower()
        tags = tags.lower()
        tags = self._getSortedListInString(tags)

        res = self.eventFiltersFind(command=command, channel=channel, actions=actions, tags=tags)
        if len(res) == 0:
            eventsFilter = ModelCapnp.Service.EventFilter.new_message()
            self.addSubItem('eventFilters', eventsFilter)
        elif len(res) == 1:
            eventsFilter = res[0]
        else:
            raise j.exceptions.Input(message="found more than 1 eventsfilter", level=1, source="", tags="", msgpub="")

        if command != '':
            eventsFilter.command = command
            changed = True
        if channel != "":
            eventsFilter.channel = channel
            changed = True

        if j.data.types.string.check(actions):
            actions = actions.split(',')

        if not j.data.types.list.check(actions):
            raise j.exceptions.Input('actions for eventFilter should be a list')

        eventsFilter.init('actions', len(actions))
        for i, action in enumerate(actions):
            eventsFilter.actions[i] = action

        if len(actions) > 0:
            changed = True

        if tags != "":
            eventsFilter.tags = tags
            changed = True
        if secrets != "":
            secrets = self._getSortedListInString(secrets)
            eventsFilter.secrets = secrets
            changed = True

        self.changed = changed

        return changed

    def _getSortedListInString(self, items):
        # sort & structure tags well
        items = [item.strip().strip(",").strip() for item in items.split(" ") if item.strip() != ""]
        items.sort()
        items = " ".join(items)
        return items

    def eventFiltersFind(self, command='', channel="", actions=[], tags=""):
        command = command.lower()
        channel = channel.lower()
        actions = [action.lower() for action in actions]
        tags = tags.lower()
        tags = self._getSortedListInString(tags)

        res = []
        for item in self.dbobj.eventFilters:
            found = True
            if command != '' and item.command != command:
                found = False
            if channel != "" and item.channel != channel:
                found = False
            if found and tags != "" and len(item.tags) > 5 and tags.find(item.tags) == -1:
                found = False
            for action in actions:
                if found and action != "" and action not in item.actions:
                    found = False
            if found:
                res.append(item)
        return res
# others

    @property
    def dictFiltered(self):
        ddict = super().dictFiltered
        # ddict = self.dbobj.to_dict()
        if "data" in ddict:
            ddict.pop("data")
        return ddict

    def _pre_save(self):
        binary = ''
        try:
            binary = self.data.to_bytes_packed()
        except Exception as e:
            self.logger.warning('Failed to save service model for service {}'.format(self))
        finally:
            self._data = None
            if binary != b'':
                self.dbobj.data = binary

    def __repr__(self):
        return "%s!%s" % (self.role, self.dbobj.name)

    def __eq__(self, other):
        if not isinstance(other, ServiceModel):
            return False
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)

    __str__ = __repr__

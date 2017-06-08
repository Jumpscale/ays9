from js9 import j
from .Service import Service
import capnp
from JumpScale9AYS.ays.lib import model_capnp as ModelCapnp
import capnp
import msgpack


class Actor():

    def __init__(self, aysrepo, template=None, model=None, name=None):
        """
        init from a template or from a model
        """

        self.aysrepo = aysrepo
        self.logger = j.atyourservice.server.logger
        self._schema = None
        self.model = None

        if template is not None:
            self._initFromTemplate(template)
        elif model is not None:
            self.model = model
        elif name is not None:
            self.loadFromFS(name=name)
        else:
            raise j.exceptions.Input(
                message="template or model or name needs to be specified when creating an actor", level=1, source="", tags="", msgpub="")

        # save this object in memory for fast access
        self.aysrepo.db.actors.actors[self.model.key] = self

    @property
    def path(self):
        return j.sal.fs.joinPaths(self.aysrepo.path, "actors", self.model.name)

    @property
    def schemaCapnpText(self):
        """
        returns capnp schema as text
        """
        path = j.sal.fs.joinPaths(self.path, "schema.capnp")
        if j.sal.fs.exists(path):
            return j.sal.fs.fileGetContents(path)
        return ""

    def loadFromFS(self, name):
        """
        get content from fs and load in object
        """
        if self.model is None:
            self.model = self.aysrepo.db.actors.new()

        actor_path = j.sal.fs.joinPaths(self.aysrepo.path, "actors", name)
        self.logger.debug("load actor from FS: %s" % actor_path)
        json = j.data.serializer.json.load(j.sal.fs.joinPaths(actor_path, "actor.json"))

        # for now we don't reload the actions codes.
        # when using distributed DB, the actions code could still be available
        actions = json.pop('actions')
        self.model.dbobj = ModelCapnp.Actor.new_message(**json)

        # need to save already here cause processActionFile is doing a find
        # and it need to be able to find this new actor model we are creating
        self.model.save()
        self.aysrepo.db.actors.actors[self.model.key] = self

        # recreate the actions code from the action.py file from the file system
        self._processActionsFile(j.sal.fs.joinPaths(actor_path, "actions.py"))
        # set recurring period
        for action in actions:
            self.model.actions[action['name']].period = action['period']
            self.model.actions[action['name']].state = action['state']
            self.model.actions[action['name']].log = action['log']

        flist_dir = j.sal.fs.joinPaths(self.path, 'flists')
        if j.sal.fs.exists(flist_dir):
            flists = self.model.dbobj.init_resizable_list('flists')
            for flist_path in j.sal.fs.listFilesInDir(flist_dir, recursive=False):
                flist = flists.add()
                flist.path = flist_path
            flists.finish()

        self.saveAll()

    def saveToFS(self):
        j.sal.fs.createDir(self.path)

        path = j.sal.fs.joinPaths(self.path, "actor.json")
        j.sal.fs.writeFile(filename=path, contents=str(self.model.dictJson), append=False)

        actionspath = j.sal.fs.joinPaths(self.path, "actions.py")
        j.sal.fs.writeFile(actionspath, self.model.actionsSourceCode)

        # path3 = j.sal.fs.joinPaths(self.path, "config.json")
        # if self.model.data != {}:
        #     j.sal.fs.writeFile(path3, self.model.dataJSON)

        path4 = j.sal.fs.joinPaths(self.path, "schema.capnp")
        if self.model.dbobj.serviceDataSchema.strip() != "":
            j.sal.fs.writeFile(path4, self.model.dbobj.serviceDataSchema)

    def saveAll(self):
        self.model.save()
        self.saveToFS()

    def update(self, reschedule=False):
        template = self.aysrepo.templateGet(self.model.dbobj.name)

        self._initParent(template)
        self._initProducers(template)
        self._initFlists(template)

        self._processActionsFile(j.sal.fs.joinPaths(template.path, "actions.py"), reschedule=reschedule)
        self._initRecurringActions(template)
        self._initTimeouts(template)
        self._initEvents(template)

        services = self.aysrepo.servicesFind(actor=self.model.name)

        if self.model.dbobj.serviceDataSchema != template.schemaCapnpText:
            # update schema in the actor itself
            self.model.dbobj.serviceDataSchema = template.schemaCapnpText
            # update existsing service schema
            for service in services:
                service.model.dbobj.dataSchema = self.model.dbobj.serviceDataSchema
                service.model._data = None  # force recreation of the capnp data object.
                # no need to manually copy the data cause they are still in the service.model.dbobj.data
                # setting _data to know force to recreate the capnp msg and fill it with content of service.model.dbobj.data
            self.processChange("dataschema")

        if self.model.dbobj.dataUI != template.dataUI:
            self.model.dbobj.dataUI = template.dataUI
            self.processChange("ui")

        self.saveToFS()
        self.model.save()

        for s in services:
            dirtyservice = False
            for action in self.model.dbobj.actions:
                if action.period > 0:
                    dirtyservice = True
                    act = s.model.actionGet(action.name)
                    act.period = action.period
                    act.log = action.log
                    act.isJob = action.isJob
                    act.timeout = action.timeout
            if dirtyservice:
                s.model.reSerialize()
                s.saveAll()

    def _initFromTemplate(self, template):
        if self.model is None:
            self.model = self.aysrepo.db.actors.new()
            self.model.dbobj.name = template.name
            self.model.dbobj.state = "new"

        # git location of actor
        self.model.dbobj.gitRepo.url = self.aysrepo.git.remoteUrl
        actorpath = j.sal.fs.joinPaths(self.aysrepo.path, "actors", self.model.name)
        self.model.dbobj.gitRepo.path = j.sal.fs.pathRemoveDirPart(self.path, actorpath)

        # process origin,where does the template come from
        # TODO: *1 need to check if template can come from other aysrepo than the one we work on right now
        self.model.dbobj.origin.gitUrl = template.giturl
        self.model.dbobj.origin.path = template.pathRelative

        self._initParent(template)
        self._initProducers(template)
        self._initFlists(template)

        self._processActionsFile(j.sal.fs.joinPaths(template.path, "actions.py"))
        self._initRecurringActions(template)
        self._initTimeouts(template)
        self._initEvents(template)

        self.model.dbobj.serviceDataSchema = template.schemaCapnpText
        self.model.dbobj.dataUI = template.dataUI

        self.saveToFS()
        self.model.save()

    def _initParent(self, template):
        parent = template.parentConfig
        if parent:
            self.model.parentSet(role=parent['role'],
                                 auto=bool(parent['auto']),
                                 optional=bool(parent.get('optional', False)),
                                 argname=parent.get('argname', parent['role'])
                                 )

    def _initProducers(self, template):
        for consume_info in template.consumptionConfig:
            self.model.producerAdd(
                role=consume_info['role'],
                min=int(consume_info['min']),
                max=int(consume_info['max']),
                auto=bool(consume_info['auto']),
                argname=consume_info.get('argname', consume_info['role'])
            )

    def _initTimeouts(self, template):
        for timeout_info in template.timeoutsConfig:
            for actionname, timeout in timeout_info.items():
                timeoutasint = j.data.types.duration.convertToSeconds(timeout)
                action_model = self.model.actions[actionname]
                action_model.timeout = timeoutasint
                ac = j.core.jobcontroller.db.actions.get(key=action_model.actionKey)
                ac.timeout = timeoutasint
                ac.save()

    def _initRecurringActions(self, template):
        for reccuring_info in template.recurringConfig:
            action_model = self.model.actions[reccuring_info['action']]
            action_model.period = j.data.types.duration.convertToSeconds(reccuring_info['period'])
            action_model.log = j.data.types.bool.fromString(reccuring_info['log'])
            ac = j.core.jobcontroller.db.actions.get(key=action_model.actionKey)
            ac.save()

    def _initEvents(self, template):
        events = self.model.dbobj.init_resizable_list('eventFilters')

        for event in template.eventsConfig:
            eventFilter = events.add()
            eventFilter.channel = event['channel']
            eventFilter.command = event['command']
            eventFilter.init('actions', len(event['actions']))
            for i, action in enumerate(event['actions']):
                eventFilter.actions[i] = action

        events.finish()

    def _initFlists(self, template):
        flists = self.model.dbobj.init_resizable_list('flists')
        for path in template.flists.values():
            dest = j.sal.fs.joinPaths(self.path, 'flists', j.sal.fs.getBaseName(path))
            dest = dest.rstrip(".tar.gz").rstrip(".tgz")
            j.sal.fs.createDir(dest)
            tar = j.tools.tarfile.get(path)
            tar.extract(dest)

            flist = flists.add()
            flist.path = dest
        flists.finish()

    def _processActionsFile(self, path, reschedule=False):
        def string_has_triple_quotes(s):
            return "'''" in s or '"""' in s

        self._out = ""

        actionmethodsRequired = ["input", "init", "install", "stop", "start", "monitor", "halt", "check_up", "check_down",
                                 "check_requirements", "cleanup", "data_export", "data_import", "uninstall", "removedata",
                                 "consume", "action_pre_", "action_post_", "init_actions_"]

        actorMethods = ["input", "build"]
        parsedActorMethods = actionmethodsRequired[:]
        if j.sal.fs.exists(path):
            content = j.sal.fs.fileGetContents(path)
        else:
            content = "class Actions():\n\n"

        if content.find("class action(ActionMethodDecorator)") != -1:
            raise j.exceptions.Input("There should be no decorator specified in %s" % self.path_actions)

        content = content.replace("from js9 import j", "")
        content = "from js9 import j\n\n%s" % content

        state = "INIT"
        amSource = ""
        actionName = ""
        amDoc = ""
        amDecorator = ""
        amMethodArgs = {}
        # DO NOT CHANGE TO USE PYTHON PARSING UTILS
        lines = content.splitlines()
        for line in lines:
            linestrip = line.strip()
            if linestrip.startswith("#"):  # general guard for comments in the beginning of the line
                continue
            if linestrip.startswith('"""') and len(linestrip.split('"""')) > 2:
                continue

            # if state == "INIT" and linestrip.startswith("class Actions"):
            if state == "INIT" and linestrip != '':
                state = "MAIN"
                continue

            if state in ["MAIN", "INIT"]:
                if linestrip == "" or linestrip[0] == "#":
                    continue

            if state == "DEF" and line[:7] != '    def' and (linestrip.startswith("@") or linestrip.startswith("def")):
                # means we are at end of def to new one
                parsedActorMethods.append(actionName)
                self._addAction(actionName, amSource, amDecorator, amMethodArgs, amDoc)
                amSource = ""
                actionName = ""
                amDoc = ""
                amDecorator = ""
                amMethodArgs = {}
                state = 'MAIN'

            if state in ["MAIN", "DEF"] and linestrip.startswith("@"):
                amDecorator = linestrip
                continue

            if state == "MAIN" and linestrip.startswith("def"):
                definition, args = linestrip.split("(", 1)
                amDoc = ""
                amSource = ""
                amMethodArgs = args.rstrip('):')
                actionName = definition[4:].strip()
                if amDecorator == "":
                    if actionName in actorMethods:
                        amDecorator = "@actor"
                    else:
                        amDecorator = "@service"
                state = "DEF"
                canbeInDocString = True

                continue

            if state == "DEF" and line.strip() == "":
                continue

            if state == "DEF" and string_has_triple_quotes(line[4:8]) and canbeInDocString:
                state = "DEFDOC"
                amDoc = ""
                continue

            if state == "DEFDOC" and string_has_triple_quotes(line[4:8]):
                state = "DEF"
                canbeInDocString = False
                continue

            if state == "DEFDOC":
                amDoc += "%s\n" % line[4:]
                continue

            if state == "DEF":
                if not string_has_triple_quotes(linestrip):
                    canbeInDocString = False
                if linestrip != line[4:].strip():
                    # means we were not rightfully intented
                    raise j.exceptions.Input(message="error in source of action from %s (indentation):\nline:%s\n%s" % (
                        self, line, content), level=1, source="", tags="", msgpub="")
                amSource += "%s\n" % line[4:]
        # process the last one
        if actionName != "":
            parsedActorMethods.append(actionName)
            self._addAction(actionName, amSource, amDecorator, amMethodArgs, amDoc)

        # check for removed actions in the actor
        self._checkRemovedActions(parsedActorMethods)

        if hasattr(self.model, 'list_actions'):
            actions_installed_names = [a.name for a in self.model.list_actions]
        else:
            actions_installed_names = [a.name for a in self.model.dbobj.actions]

        for actionname in actionmethodsRequired:

            if actionname not in actions_installed_names:
                # not found

                # check if we find the action in our default actions, if yes use that one
                if actionname in j.atyourservice.server.baseActions:
                    actionobj, actionmethod = j.atyourservice.server.baseActions[actionname]
                    self.model.actionAdd(name=actionname, key=actionobj.key)
                else:
                    if actionname == "input":
                        amSource = "return None"
                        self._addAction(actionName="input", amSource=amSource,
                                        amDecorator="actor", amMethodArgs="job", amDoc="")
                    else:
                        self._addAction(actionName=actionname, amSource="",
                                        amDecorator="service", amMethodArgs="job", amDoc="")

        # mode list from memory into capnp struct
        self.model.reSerialize()

        # change if  we need to fire processChange jobs
        for action in self.model.dbobj.actions:
            self._check_change(action, reschedule=reschedule)

    def _checkRemovedActions(self, parsedMethods):
        for action in self.model.actionsSortedList:
            if action not in parsedMethods:
                self.processChange('action_del_%s' % action)

    def _addAction(self, actionName, amSource, amDecorator, amMethodArgs, amDoc):

        if amSource == "":
            amSource = "pass"

        amDoc = amDoc.strip()

        # THIS COULD BE DANGEROUS !!! (despiegk)
        amSource = amSource.strip(" \n")

        ac = j.core.jobcontroller.db.actions.new()
        ac.dbobj.code = amSource
        ac.dbobj.actorName = self.model.name
        ac.dbobj.doc = amDoc
        ac.dbobj.name = actionName
        ac.dbobj.args = amMethodArgs
        ac.dbobj.lastModDate = j.data.time.epoch
        ac.dbobj.origin = "actoraction:%s:%s" % (self.model.dbobj.name, actionName)
        if not j.core.jobcontroller.db.actions.exists(ac.key):
            # will save in DB
            ac.save()
        else:
            ac = j.core.jobcontroller.db.actions.get(key=ac.key)
        self.model.actionAdd(name=actionName, key=ac.key, isJob=('job' in amMethodArgs))

    def _check_change(self, actionObj, reschedule=False):
        """
        @param actionName = actionName
        @param action is the action object
        """
        if actionObj.state == "new":
            self.processChange("action_new_%s" % actionObj.name, reschedule=reschedule)
        else:
            self.processChange("action_mod_%s" % actionObj.name, reschedule=reschedule)

    def processChange(self, changeCategory, reschedule=False):
        """
        template action change
        categories :
            - dataschema
            - ui
            - config
            - action_new_actionname
            - action_mod_actionname
            - action_del_actionname
        """
        # self.logger.debug('process change for %s (%s)' % (self, changeCategory))
        if changeCategory == 'dataschema':
            # TODO
            pass

        elif changeCategory == 'ui':
            # TODO
            pass

        elif changeCategory == 'config':
            # TODO
            pass

        elif changeCategory.find('action_new') != -1:
            # TODO
            pass
        elif changeCategory.find('action_mod') != -1:
            # TODO
            pass
        elif changeCategory.find('action_del') != -1:
            action_name = changeCategory.split('action_del_')[1]
            self.model.actionDelete(action_name)

        self.saveAll()

        for service in self.aysrepo.servicesFind(actor=self.model.name):
            service.processChange(actor=self, changeCategory=changeCategory, reschedule=reschedule)

# SERVICE

    async def asyncServiceCreate(self, instance="main", args={}):
        instance = instance
        service = self.aysrepo.serviceGet(role=self.model.role, instance=instance, die=False)
        if service is not None:
            service._check_args(self, args)
            return service

        # checking if we have the service on the file system
        target = "%s!%s" % (self.model.name, instance)
        services_dir = j.sal.fs.joinPaths(self.aysrepo.path, 'services')
        results = j.sal.fswalker.walkExtended(services_dir, files=False, dirPattern=target)
        if len(results) > 1:
            raise j.exceptions.RuntimeError("found more then one service directory for %s" % target)
        elif len(results) == 1:
            service = Service.init_from_fs(aysrepo=self.aysrepo, path=results[0])
        else:
            service = await Service.init_from_actor(aysrepo=self.aysrepo, actor=self, name=instance, args=args)

        return service

    def serviceCreate(self, instance='main', args={}):
        """
        same call as asyncServiceCreate but synchronous. we expose this so user can use this method in service actions.
        """
        return j.tools.async.wrappers.sync(self.asyncServiceCreate(instance=instance, args=args))

    @property
    def services(self):
        """
        return a list of instance name for this template
        """
        return self.aysrepo.servicesFind(actor=self.model.dbobj.name)


# GENERIC
    def __repr__(self):
        return "actor: %-15s" % (self.model.name)

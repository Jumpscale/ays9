from js9 import j
import yaml
import re
from .utils import validate_service_name, validate_bp_yaml, validate_bp_format

class Blueprint:
    """
    """

    def __init__(self, aysrepo, path="", content=""):
        self.logger = j.logger.get('j.atyourservice.server.blueprint')
        self.aysrepo = aysrepo
        self.path = path
        self.active = True
        self.models = []  # can be actions or services or recurring
        self.actions = []
        self.eventFilters = []
        self._contentblocks = []


        if path != "":
            self.name = j.sal.fs.getBaseName(path)
            if self.name[0] == "_":
                self.active = False
            self.name = self.name.lstrip('_')
            self.content = j.sal.fs.fileGetContents(path)
        else:
            self.name = 'unknown'
            self.content = content

        self.is_valid, self.valid_msg = validate_bp_yaml(name=self.name, content=self.content, logger=self.logger)

        if self.is_valid:
            decoded = j.data.serializer.yaml.ordered_load(self.content, yaml.SafeLoader) or {}
            for key, value in decoded.items():
                self.models.append({key: value})

            self.hash = j.data.hash.md5_string(self.content)
            self.is_valid, self.valid_msg = validate_bp_format(path=self.path, models=self.models, aysrepo=self.aysrepo, logger=self.logger)

    async def load(self, role="", instance="", context=None):
        self.actions = []
        self.eventFilters = []
        for model in self.models:
            if model is not None:

                if "actions" in model:
                    # found action need to add them to blueprint
                    for actionModel in model["actions"]:
                        if 'actor' not in actionModel:
                            actor0 = ""
                        else:
                            actor0 = actionModel["actor"]
                        if 'service' not in actionModel:
                            service0 = ""
                        else:
                            service0 = actionModel["service"]
                        if 'recurring' not in actionModel:
                            recurring0 = ""
                        else:
                            recurring0 = actionModel["recurring"]
                        force0 = bool(actionModel.get('force', False))

                        if "action" not in actionModel:
                            raise j.exceptions.Input(message="need to specify action.",
                                                     level=1, source="", tags="", msgpub="")

                        actions = [item.strip() for item in actionModel["action"].split(",") if item.strip() != ""]

                        for actionName in actions:
                            self.actions.append({
                                # 'service_key': serviceObj.model.key,
                                'service': service0,
                                'actor': actor0,
                                'action_name': actionName,
                                'recurring_period': recurring0,
                                'force': force0,
                            })

                elif "eventfilters" in model:
                        # found action need to add them to blueprint
                    for obj in model["eventfilters"]:
                        if 'actor' not in obj:
                            actor0 = ""
                        else:
                            actor0 = obj["actor"]
                        if 'service' not in obj:
                            service0 = ""
                        else:
                            service0 = obj["service"]
                        if 'channel' not in obj:
                            channel0 = ""
                        else:
                            channel0 = obj["channel"]
                        if 'command' not in obj:
                            cmd0 = ""
                        else:
                            cmd0 = obj["command"]
                        if 'secret' not in obj:
                            secret0 = ""
                        else:
                            secret0 = obj["secret"]
                        if 'actions' not in obj:
                            action0 = []
                        else:
                            action0 = obj["actions"]

                        self.eventFilters.append({
                            'service': service0,
                            'actor': actor0,
                            'channel': channel0,
                            'command': cmd0,
                            'secret': secret0,
                            'action_name': action0,
                        })

                else:
                    for key, item in model.items():
                        if key.find("__") == -1:
                            raise j.exceptions.Input(
                                "Key in blueprint is not right format, needs to be $aysname__$instance, found:'%s'" % key)
                        actorname, bpinstance = key.split("__", 1)
                        if ":" in bpinstance:
                            raise j.exceptions.Input("service names ({}) cannot contain colons (:)".format(bpinstance))
                        if ":" in actorname:
                            raise j.exceptions.Input("actor names ({}) cannot contain colons (:)".format(actorname))

                        if instance != "" and bpinstance != instance:
                            self.logger.info(
                                "ignore load from blueprint for: %s:%s" % (actorname, bpinstance))
                            continue

                        if actorname.find(".") != -1:
                            rolefound, _ = actorname.split(".", 1)
                        else:
                            rolefound = actorname

                        if role != "" and role != rolefound:
                            self.logger.info(
                                "ignore load from blueprint based on role for: %s:%s" % (actorname, bpinstance))
                            continue

                        # check if we can find actorname and if not then check if there is a blueprint.  name...
                        if not self.aysrepo.templateExists(actorname) and not actorname.startswith('blueprint.'):
                            blueaysname = 'blueprint.%s' % actorname
                            if self.aysrepo.templateExists(blueaysname):
                                actorname = blueaysname

                        if not self.aysrepo.templateExists(actorname):
                            raise j.exceptions.Input(message="Cannot find actor:%s" %
                                                     actorname, level=1, source="", tags="", msgpub="")
                        actor = self.aysrepo.actorGet(actorname, context=context)
                        args = {} if item is None else item
                        await actor.asyncServiceCreate(instance=bpinstance, args=args, context=context)

        msg = "Blueprint {} executed".format(self.name)
        # first we had to make sure all services do exist, then we can add these properties
        for idx, action_info in enumerate(self.actions):
            if action_info['action_name'] == "delete":
                for service in self.aysrepo.servicesFind(name=action_info['service'], actor=action_info['actor']):
                    ok, oktodeletemsg = await service.checkDelete()
                    if not ok:
                        msg += "\n- Skipped delete action for service {}: {}".format(service.name, oktodeletemsg)
                        self.logger.warning(msg)
                        self.actions.pop(idx)  # we pop the delete action here if you don't want to raise exception and continue with the rest of actions.

        for action_info in self.actions:
            for service in self.aysrepo.servicesFind(name=action_info['service'], actor=action_info['actor']):
                service.scheduleAction(action_info['action_name'], period=action_info['recurring_period'], force=action_info['force'])
                service.saveAll()

        for event_filter in self.eventFilters:
            for service in self.aysrepo.servicesFind(name=action_info['service'], actor=action_info['actor']):
                service.model.eventFilterSet(
                    channel=event_filter['channel'], actions=event_filter['action_name'],
                    command=event_filter['command'], secrets=event_filter['secret'])
                service.saveAll()
        return msg

    @property
    def services(self):
        services = []
        for model in self.models:

            if model is not None:
                for key in model.keys():

                    aysname, aysinstance = key.split("__", 1)
                    if aysname.find(".") != -1:
                        rolefound, _ = aysname.split(".", 1)
                    else:
                        rolefound = aysname

                    service = self.aysrepo.serviceGet(role=rolefound, instance=aysinstance, die=False)
                    if service:
                        services.append(service)

        return services

    def disable(self):
        if self.active:
            base = j.sal.fs.getBaseName(self.path)
            dirpath = j.sal.fs.getDirName(self.path)
            newpath = j.sal.fs.joinPaths(dirpath, "_%s" % base)
            j.sal.fs.moveFile(self.path, newpath)
            self.path = newpath
            self.active = False

    def enable(self):
        if self.active is False:
            base = j.sal.fs.getBaseName(self.path)
            if base.startswith("_"):
                base = base[1:]
            dirpath = j.sal.fs.getDirName(self.path)
            newpath = j.sal.fs.joinPaths(dirpath, base)
            j.sal.fs.moveFile(self.path, newpath)
            self.path = newpath
            self.active = True




    def validate(self):
        return self.is_valid, self.valid_msg

    def __str__(self):
        return "%s:%s" % (self.name, self.hash)

    __repr__ = __str__

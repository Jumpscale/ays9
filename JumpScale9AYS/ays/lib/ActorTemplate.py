from js9 import j
from collections import OrderedDict


class ActorTemplate():

    def __init__(self, path, template_repo=None):
        self.logger = j.logger.get('j.atyourservice.server')

        if template_repo is not None:
            if j.sal.fs.exists(path=path):
                # we know its absolute
                relpath = j.sal.fs.pathRemoveDirPart(
                    path, template_repo.git.BASEDIR, removeTrailingSlash=True)
                # path is now relative path
            else:
                relpath = path
                path = j.sal.fs.joinPaths(template_repo.git.BASEDIR, path)
                if not j.sal.fs.exists(path=path):
                    raise j.exceptions.Input(
                        "Cannot find path for template:%s" % path)
        else:
            relpath = ""

        self.pathRelative = relpath

        self.path = path

        base = j.sal.fs.getBaseName(path)
        self.name = base
        self.template_repo = template_repo
        if template_repo is not None:
            self.giturl = self.template_repo.git.remoteUrl
            self.gitpath = self.template_repo.git.BASEDIR
        else:
            self.giturl = ""
            self.gitpath = ""

        # use inotify to watch for the template changes
        watcher = j.atyourservice.server.watcher
        watcher_mask = j.atyourservice.server.watcher_mask
        watcher.add_watch(path.encode(), watcher_mask)

    @property
    def role(self):
        return self.name.split('.')[0]

    @property
    def schemaCapnpText(self):
        """
        returns capnp schema as text
        """
        path = j.sal.fs.joinPaths(self.path, "schema.capnp")
        if j.sal.fs.exists(path):
            return j.sal.fs.fileGetContents(path)
        return ""

    @property
    def schema(self):
        try:
            return j.data.capnp.getSchemaFromText(self.schemaCapnpText, name="Schema")
        except Exception as e:
            errmsg = str(e).split("stack:")[0]
            msg = "Could not load capnp schema for:%s\n" % self
            msg += "- path: %s\n" % self.path
            msg += "CapnpError:\n%s" % errmsg
            raise j.exceptions.Input(message=msg, level=1, source="ays.template", tags="", msgpub="")

    @property
    def configDict(self):
        path = j.sal.fs.joinPaths(self.path, "config.yaml")
        path2 = j.sal.fs.joinPaths(self.path, "config.json")
        if j.sal.fs.exists(path, followlinks=True):
            ddict = j.data.serializer.yaml.load(path) or {}
        elif j.sal.fs.exists(path2, followlinks=True):
            ddict = j.data.serializer.json.load(path) or {}
        else:
            ddict = {}

        if "events" in ddict:
            for x in range(0, len(ddict["events"])):
                ddict["events"][x] = j.data.capnp.tools.listInDictCreation(
                    ddict["events"][x], "actions")
                ddict["events"][x] = j.data.capnp.tools.listInDictCreation(
                    ddict["events"][x], "secrets")
        return ddict

    @property
    def configJSON(self):
        ddict2 = OrderedDict(self.configDict)
        return j.data.serializer.json.dumps(ddict2, sort_keys=True, indent=True)

    @property
    def configYAML(self):
        ddict2 = OrderedDict(self.configDict)
        return j.data.serializer.yaml.dumps(ddict2)

    @property
    def dataUI(self):
        path = j.sal.fs.joinPaths(self.path, "ui.py")
        if j.sal.fs.exists(path, followlinks=True):
            return j.sal.fs.fileGetContents(path)
        return ""

    @property
    def recurringConfig(self):
        return self.configDict.get("recurring", {})

    @property
    def eventsConfig(self):
        return self.configDict.get("events", {})

    @property
    def linksConfig(self):
        return self.configDict.get("links", {})

    @property
    def parentConfig(self):
        result = self.configDict.get("links", {})
        result = result[0].get('parent', {}) if isinstance(result, list) else result.get('parent', {})
        return result

    @property
    def timeoutsConfig(self):
        return self.configDict.get("timeouts", {})

    @property
    def consumptionConfig(self):
        result = self.configDict.get("links", {})
        result = result[0].get('consume', {}) if isinstance(result, list) else result.get('consume', {})
        return result

    @property
    def flists(self):
        flists = {}
        for flist_path in j.sal.fs.listFilesInDir(self.path, recursive=False, filter="flist-*.tar.gz"):
            name = j.sal.fs.getBaseName(flist_path)
            name = name.lstrip('flist-').rstrip('db.tar.gz')
            flists[name] = flist_path
        return flists

    def __repr__(self):
        return "actortemplate: %-25s:%s" % (self.path, self.name)

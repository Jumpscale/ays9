"""
Utilites modules for ays libs
"""
from js9 import j

import yaml
import os
import fcntl
import re

DEFAULT_LOGGER = j.logger.get('j.atyourservice.server.utils')

def validate_service_name(name, logger=None):
    """
    Validates that services have valid name

    Returns a tuple of (True/False, message)
    """
    if logger is None:
        logger = DEFAULT_LOGGER
    message = ''
    if not re.sub("[-_.]", "", name).isalnum():
        message = "Service instance name should be digits or alphanumeric. you passed [%s]" % name
        logger.error(message)
        return False, message
    return True, message


def validate_bp_yaml(name, content, logger=None):
    """
    Validates YAML syntax
    """
    if logger is None:
        logger = DEFAULT_LOGGER

    try:
        j.data.serializer.yaml.loads(content)
        return True, "yaml is valid"
    except yaml.YAMLError:
        message = 'Yaml format is not valid for %s please fix this to continue' % name
        logger.error(message)
        return False, message


def validate_bp_format(path, models, aysrepo, logger=None):
    """
    Validates blueprint format
    """
    if logger is None:
        logger = DEFAULT_LOGGER

    for model in models:
        if model is None:
            continue

        if model and not j.data.types.dict.check(model):
            message = "Bad formatted blueprint: %s" % path
            logger.error(message)
            return False, message

        for key in model.keys():

            # this two blocks doesn't have the same format as classic service declaration
            if key in ['actions', 'eventfilters']:
                if not j.data.types.list.check(model[key]):
                    message = "%s should be a list of dictionary: found %s" % (key, type(model[key]))
                    logger.error(message)
                    return False, message
            else:
                if key.find("__") == -1:
                    message = "Key in blueprint is not right format, needs to be $aysname__$instance, found:'%s'" % key
                    logger.error(message)
                    return False, message

                aysname, instance = key.split("__", 1)
                if aysname not in aysrepo.templates:
                    message = "Service template %s not found. Can't execute this blueprint" % aysname
                    logger.error(message)
                    return False, message

                return validate_service_name(name=instance)

    return True, 'Blueprint format is valid'

def searchLocationsOnMac(path, find_cmd, link_cmd, target_repos=True):
    res = []
    rc, out, err = j.sal.process.execute(find_cmd, die=False, showout=False)
    for location in out.splitlines():
        if j.sal.fs.isLink(location):
            rc, out, err = j.sal.process.execute(link_cmd%location, die=False, showout=False)
            location = out
        if target_repos:
            location = location.split(".ays")[0]
            if location.startswith(".") or location.startswith("_"):
                continue
        res.append(location)
    return res

def searchLocationsOnLinux(path, cmd, target_repos=True):
    res = []
    rc, out, err = j.sal.process.execute(cmd, die=False, showout=False)
    if target_repos:
        for location in out.splitlines():
            location = lcation.split(".ays")[0]
            if location.startswith(".") or location.startswith("_"):
                continue
            res.append(location)
    else:
        res = out.splitlines()
    return res

class Lock:
    def __init__(self, path):
        self._path = path

    def __enter__(self):
        self._fd = os.open(self._path, os.O_CREAT | os.O_WRONLY)
        fcntl.lockf(self._fd, fcntl.LOCK_EX)

    def __exit__(self, *exc_info):
        fcntl.lockf(self._fd, fcntl.LOCK_UN)
        os.close(self._fd)

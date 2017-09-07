from js9 import j

def init_actions_(service, args):
    dependencies = {
        'enable': ['install'],
        'disable': ['install']
    }
    return dependencies


def input(job):
    service = job.service
    if job.model.args.get('location', "") == "":
        raise j.exceptions.Input("Location argument cannot be empty. Cannot continue input of %s" % service)


def init(job):
    service = job.service
    if 'g8client' not in service.producers:
        raise j.exceptions.AYSNotFound("No producer g8client found. Cannot continue init of %s" % service)
    g8client = service.producers["g8client"][0]

    users = service.model.data.uservdc
    for user in users:
        uservdc = service.aysrepo.serviceGet('uservdc', user.name)
        service.consume(uservdc)

    accountservice = None
    if service.model.data.account == "":
        service.model.data.account = g8client.model.data.account
    acc = service.model.data.account
    # get the service if it exists or create it
    # search for that acc.
    try:
        accountservice = service.aysrepo.serviceGet("account", acc)
    except:
        accargs = {'g8client': g8client.name}
        accountactor = service.aysrepo.actorGet("account")
        accountservice = accountactor.serviceCreate(g8client.model.data.account, accargs)
        accountservice.saveAll()
    service.consume(accountservice)

    service.saveAll()


def authorization_user(space, service):
    authorized_users = space.authorized_users
    userslist = service.producers.get('uservdc', [])
    user_exists = True
    users = []
    for u in userslist:
        if u.model.data.provider != '':
            users.append(u.model.dbobj.name + "@" + u.model.data.provider)
        else:
            users.append(u.model.dbobj.name)

    # Authorize users
    for user in users:
        if user not in authorized_users:
            user_exists = False
        for uvdc in service.model.data.uservdc:
            if uvdc.name == user.split('@')[0]:
                if user_exists:
                    space.update_access(username=user, right=uvdc.accesstype)
                else:
                    space.authorize_user(username=user, right=uvdc.accesstype)

    # Unauthorize users not in the schema
    for user in authorized_users:
        if user not in users:
            space.unauthorize_user(username=user)


def install(job):
    service = job.service
    if 'g8client' not in service.producers:
        raise j.exceptions.AYSNotFound("No producer g8client found. Cannot continue install of %s" % service)
    g8client = service.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(service.model.data.account)

    # Set limits
    # if space does not exist, it will create it
    externalnetworkId = service.model.data.externalNetworkID
    externalnetworkId = None if externalnetworkId == -1 else externalnetworkId
    space = acc.space_get(name=service.model.dbobj.name,
                          location=service.model.data.location,
                          create=True,
                          maxMemoryCapacity=service.model.data.maxMemoryCapacity,
                          maxVDiskCapacity=service.model.data.maxDiskCapacity,
                          maxCPUCapacity=service.model.data.maxCPUCapacity,
                          maxNumPublicIP=service.model.data.maxNumPublicIP,
                          maxNetworkPeerTransfer=service.model.data.maxNetworkPeerTransfer,
                          externalnetworkId=externalnetworkId
                          )

    # add space ID to data
    service.model.data.cloudspaceID = space.model['id']
    service.model.save()
    authorization_user(space, service)

    # update capacity incase cloudspace already existed update it
    space.model['maxMemoryCapacity'] = service.model.data.maxMemoryCapacity
    space.model['maxVDiskCapacity'] = service.model.data.maxDiskCapacity
    space.model['maxNumPublicIP'] = service.model.data.maxNumPublicIP
    space.model['maxCPUCapacity'] = service.model.data.maxCPUCapacity
    space.model['maxNetworkPeerTransfer'] = service.model.data.maxNetworkPeerTransfer
    space.save()


def get_user_accessright(username, service):
    for u in service.model.data.uservdc:
        if u.name == username:
            return u.accesstype


def processChange(job):
    service = job.service

    args = job.model.args
    category = args.pop('changeCategory')

    if 'g8client' not in service.producers:
        raise j.exceptions.AYSNotFound("No producer g8client found. Cannot continue processChange of %s" % service)
    g8client = service.producers["g8client"][0]

    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(service.model.data.account)

    # Get given space, raise error if not found
    space = acc.space_get(name=service.model.dbobj.name,
                          location=service.model.data.location,
                          create=False)
    if category == "dataschema" and service.model.actionsState['install'] == 'ok':
        for key, value in args.items():
            if key == 'uservdc':
                # value is a list of (uservdc)
                if not isinstance(value, list):
                    raise j.exceptions.Input(message="Value is not a list.")
                if 'uservdc' in service.producers:
                    for s in service.producers['uservdc']:
                        if not any(v['name'] == s.name for v in value):
                            service.model.producerRemove(s)
                        for v in value:
                            accessRight = v.get('accesstype', '')
                            if v['name'] == s.name and accessRight != get_user_accessright(s.name, service):
                                name = s.name + '@' + s.model.data.provider if s.model.data.provider else s.name
                                space.update_access(name, accessRight)
                for v in value:
                    userservice = service.aysrepo.serviceGet('uservdc', v['name'])
                    if userservice not in service.producers.get('uservdc', []):
                        service.consume(userservice)
            elif key == 'location' and service.model.data.location != value:
                raise RuntimeError("Cannot change attribute location")
            setattr(service.model.data, key, value)

        authorization_user(space, service)

        # update capacity incase cloudspace already existed update it
        space.model['maxMemoryCapacity'] = service.model.data.maxMemoryCapacity
        space.model['maxVDiskCapacity'] = service.model.data.maxDiskCapacity
        space.model['maxNumPublicIP'] = service.model.data.maxNumPublicIP
        space.model['maxCPUCapacity'] = service.model.data.maxCPUCapacity
        space.save()

        service.save()


def uninstall(job):
    service = job.service
    if 'g8client' not in service.producers:
        raise j.exceptions.AYSNotFound("No producer g8client found. Cannot continue uninstall of %s" % service)

    g8client = service.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(service.model.data.account)
    space = acc.space_get(service.model.dbobj.name, service.model.data.location)
    space.delete()

def enable(job):
    """
    This action will enable the vdc.
    """
    service = job.service

    if 'g8client' not in service.producers:
        raise j.exceptions.AYSNotFound("No producer g8client found. Cannot continue enabling  %s" % service)

    g8client = service.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(service.model.data.account)
    # Get space, raise error if not found
    space = acc.space_get(name=service.model.dbobj.name,
                          location=service.model.data.location,
                          create=False)
    space.enable('The space should be enabled.')
    service.model.data.disabled = False
    service.saveAll()

def disable(job):
    """
    This action will disable the vdc.
    """
    service = job.service

    if 'g8client' not in service.producers:
        raise j.exceptions.AYSNotFound("No producer g8client found. Cannot continue disabling  %s" % service)

    g8client = service.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(service.model.data.account)
    # Get space, raise error if not found
    space = acc.space_get(name=service.model.dbobj.name,
                          location=service.model.data.location,
                          create=False)
    space.disable('The space should be disabled.')
    service.model.data.disabled = True
    service.saveAll()

from js9 import j


def init_actions_(service, args):
    dependencies = {
        'list_disks': ['init'],
        'get_consumption': ['install']
    }
    return dependencies


def init(job):
    service = job.service
    if 'g8client' not in service.producers:
        raise j.exceptions.AYSNotFound("No producer g8client found. Cannot continue init of %s" % service)

    users = service.model.data.accountusers
    for user in users:
        uservdc = service.aysrepo.serviceGet('uservdc', user.name)
        service.consume(uservdc)

    service.saveAll()

def authorization_user(account, service, update=False):
    authorized_users = account.authorized_users

    userslist = service.producers.get('uservdc', [])
    users = []
    for u in userslist:
        if u.model.data.provider != '':
            users.append(u.model.dbobj.name + "@" + u.model.data.provider)
        else:
            users.append(u.model.dbobj.name)

    # Authorize users
    for user in users:
        if user not in authorized_users:
            for uvdc in service.model.data.accountusers:
                if uvdc.name == user.split('@')[0]:
                    if uvdc.accesstype:
                        account.authorize_user(username=user, right=uvdc.accesstype)
                    else:
                        account.authorize_user(username=user)

    if update:
        # Unauthorize users not in the schema
        for user in authorized_users:
            if user not in users:
                account.unauthorize_user(username=user)

def get_user_accessright(username, service):
    for u in service.model.data.accountusers:
        if u.name == username:
            return u.accesstype

def install(job):
    service = job.service
    if 'g8client' not in service.producers:
        raise j.exceptions.AYSNotFound("No producer g8client found. Cannot continue install of %s" % service)
    g8client = service.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)

    # Set limits
    # if account does not exist, it will create it
    account = cl.account_get(name=service.model.dbobj.name,
                             create=True,
                             maxMemoryCapacity=service.model.data.maxMemoryCapacity,
                             maxVDiskCapacity=service.model.data.maxDiskCapacity,
                             maxCPUCapacity=service.model.data.maxCPUCapacity,
                             maxNumPublicIP=service.model.data.maxNumPublicIP,
                             )
    service.model.data.accountID = account.model['id']
    service.model.save()

    authorization_user(account, service, False)
    # Unauthorize users not in the schema
    # THIS FUNCTIONALITY IS DISABLED UNTIL OVC DOESN'T REQUIRE USERS TO BE ADMIN


    # update capacity in case account already existed
    account.model['maxMemoryCapacity'] = service.model.data.maxMemoryCapacity
    account.model['maxVDiskCapacity'] = service.model.data.maxDiskCapacity
    account.model['maxNumPublicIP'] = service.model.data.maxNumPublicIP
    account.model['maxCPUCapacity'] = service.model.data.maxCPUCapacity
    account.save()


def processChange(job):
    service = job.service

    if 'g8client' not in service.producers:
        raise j.exceptions.AYSNotFound("No producer g8client found. Cannot continue processChange of %s" % service)

    g8client = service.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    account = cl.account_get(name=service.model.dbobj.name, create=False)

    args = job.model.args
    category = args.pop('changeCategory')
    if category == "dataschema" and service.model.actionsState['install'] == 'ok':
        for key, value in args.items():
            if key == 'accountusers':
                # value is a list of (uservdc)
                if not isinstance(value, list):
                    raise j.exceptions.Input(message="Value is not a list.")

                for s in service.producers['uservdc']:
                    if not any(v['name'] == s.name for v in value):
                        service.model.producerRemove(s)
                    for v in value:
                        accessRight = v.get('accesstype', '')
                        if v['name'] == s.name and accessRight != get_user_accessright(s.name, service) and accessRight:
                            name = s.name + '@' + s.model.data.provider if s.model.data.provider else s.name
                            account.update_access(name, v['accesstype'])

                for v in value:
                    userservice = service.aysrepo.serviceGet('uservdc', v['name'])
                    if userservice not in service.producers.get('uservdc', []):
                        service.consume(userservice)
            setattr(service.model.data, key, value)

        authorization_user(account, service, True)

        # update capacity
        account.model['maxMemoryCapacity'] = service.model.data.maxMemoryCapacity
        account.model['maxVDiskCapacity'] = service.model.data.maxDiskCapacity
        account.model['maxNumPublicIP'] = service.model.data.maxNumPublicIP
        account.model['maxCPUCapacity'] = service.model.data.maxCPUCapacity
        account.save()

        service.save()


def uninstall(job):
    service = job.service
    if 'g8client' not in service.producers:
        raise j.exceptions.AYSNotFound("No producer g8client found. Cannot continue uninstall of %s" % service)

    g8client = service.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(service.model.dbobj.name)
    acc.delete()


def list_disks(job):
    service = job.service
    g8client = service.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    account = cl.account_get(name=service.model.dbobj.name)
    service.model.disks = account.disks
    service.save()


def get_consumption(job):
    import datetime
    service = job.service
    g8client = service.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    account = cl.account_get(name=service.model.dbobj.name)
    if not service.model.data.consumptionFrom and not service.model.data.consumptionTo:
        service.model.data.consumptionFrom = account.model['creationTime']
        end = datetime.datetime.fromtimestamp(service.model.data.consumptionFrom) + datetime.timedelta(hours=1)
        service.model.data.consumptionTo = end.timestamp()
    service.model.data.consumptionData = account.get_consumption(service.model.data.consumptionFrom, service.model.data.consumptionTo)

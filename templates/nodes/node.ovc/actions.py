def _get_cloud_space(service):
    vdc = service.parent

    if 'g8client' not in vdc.producers:
        raise j.exceptions.AYSNotFound("No producer g8client found. Cannot continue %s" % service)

    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)
    return space


def _create_machine(service, space):
    vdc = service.parent
    image_names = [i['name'] for i in space.images]
    if service.model.data.osImage not in image_names:
        raise j.exceptions.NotFound('Image %s not available for vdc %s' % (service.model.data.osImage, vdc.name))
    machine = space.machine_create(name=service.name,
                                   image=service.model.data.osImage,
                                   memsize=service.model.data.memory,
                                   disksize=service.model.data.bootdiskSize,
                                   sizeId=service.model.data.sizeID if service.model.data.sizeID >= 0 else None,
                                   stackId=service.model.data.stackID if service.model.data.stackID >= 0 else None)
    return machine


def _configure_ports(service, machine):
    ssh_present = any([port_forward for port_forward in service.model.data.ports if port_forward.startswith('22')])

    # check if the machine was created before and has a port forward
    # for port 22 to avoid multiple port forward for the same port
    if not ssh_present:
        for port_forward in machine.portforwardings:
            if int(port_forward["localPort"]) == 22:
                ssh_present = True
                break

    data = j.data.serializer.json.loads(service.model.dataJSON)
    ports = data.get('ports', []) if ssh_present else data.get('ports', []) + ['22']
    forwarded_ports = machine.portforwardings
    for port in ports:
        skip = False
        port_parts = port.split(':')
        if len(port_parts) == 2:
            public_port, local_port = port_parts
            # Check if the same ports were already forwarded before so we can skip it
            for port_forward in forwarded_ports:
                if public_port == port_forward['publicPort'] and local_port == port_forward['localPort']:
                    skip = True
                    break
        else:
            local_port = port
            public_port = None

        if not skip:
            machine.create_portforwarding(publicport=public_port, localport=local_port, protocol='tcp')

    # Get all created ports forwarding (from current model + previously created if any)
    ports = []
    for port_forward in machine.portforwardings:
        port_added = "{public}:{local}".format(public=port_forward["publicPort"], local=port_forward["localPort"])
        ports.append(port_added)

    # Looking in the parents chain is needed when we have nested nodes (like a docker node on top of an ovc node)
    # we need to find all the ports forwarding chain to reach the inner most node.
    ssh_port = '22'

    for port in ports:
        src, _, dst = port.partition(':')
        if ssh_port == dst:
            ssh_port = src
            break

    service.model.data.sshPort = int(ssh_port)
    service.model.data.ports = ports


def _check_ssh_authorization(service, machine):
    if not service.model.data.sshAuthorized:
        # Authorize ssh key into the machine
        _, vm_info = machine.get_machine_ip()
        if vm_info['status'] not in ['HALTED', 'PAUSED']:
            prefab = _ssh_authorize(service, vm_info)
            return prefab
    return False


def _ssh_authorize(service, vm_info):
    if 'sshkey' not in service.producers:
        raise j.exceptions.AYSNotFound("No sshkey service consumed. please consume an sshkey service")
    service.logger.info("Authorizing ssh key to machine {}".format(vm_info['name']))

    sshkey = service.producers['sshkey'][0]
    key_path = j.sal.fs.joinPaths(sshkey.path, 'id_rsa')
    password = vm_info['accounts'][0]['password'] if vm_info['accounts'][0]['password'] != '' else None
    # used the login/password information from the node to first connect to the node and
    # then authorize the sshkey for root
    executor = j.tools.executor.getSSHBased(addr=service.model.data.ipPublic, port=service.model.data.sshPort,
                                            login=vm_info['accounts'][0]['login'], passwd=password,
                                            allow_agent=True, look_for_keys=True, timeout=5, usecache=False,
                                            passphrase=None, key_filename=key_path)
    executor.prefab.ssh.authorize("root", sshkey.model.data.keyPub)
    service.model.data.sshAuthorized = True
    service.saveAll()
    return executor.prefab


def _configure_disks(service, machine, prefab):

    # GET THE available devices on the system and bind them to services
    # if available instead of creating disks
    rc, out, err = prefab.core.run("lsblk -J", die=False)
    if rc != 0:
        raise j.exceptions.RuntimeError("Unexpected Error: {}".format(err))
    jsonout = j.data.serializer.json.loads(out)
    available_devices = [x['name'] for x in jsonout['blockdevices'] if
                         x['mountpoint'] is None and x['type'] == 'disk' and 'children' not in x]  # should be only 1

    datadisks = service.producers.get('disk', [])
    takendevices = [x.model.data.devicename for x in datadisks if x.model.data.devicename != '']

    # Add disks to machine if they aren't there else logically bind to any of them.
    for data_disk in datadisks:
        disk_args = data_disk.model.data
        if data_disk.model.data.devicename == '' and len(available_devices):
            data_disk.model.data.devicename = available_devices.pop(0)
            takendevices.append(data_disk.model.data.devicename)

        else:
            disk_id = machine.add_disk(name=data_disk.model.dbobj.name,
                                       description=disk_args.description,
                                       size=disk_args.size,
                                       type=disk_args.type.upper(),
                                       ssdSize=disk_args.ssdSize)

            machine.disk_limit_io(disk_id, disk_args.maxIOPS)
            rc, out, err = prefab.core.run("lsblk -J", die=False)
            if rc != 0:
                raise j.exceptions.RuntimeError("Unexpected Error: {}".format(err))
            jsonout = j.data.serializer.json.loads(out)
            available_devices = [x['name'] for x in jsonout['blockdevices'] if
                                 x['mountpoint'] is None and x['type'] == 'disk' and 'children' not in x and x[
                                     'name'] not in takendevices]
            data_disk.model.data.devicename = available_devices.pop(0)
            takendevices.append(data_disk.model.data.devicename)

        data_disk.saveAll()


def input(job):
    # support for using node in blueprint to specify the parent.
    # we change it to point to os so it match the requirment of the schema
    args = job.model.args
    if 'node' in args:
        args['os'] = args['node']
        del args['node']
    return args


def init(job):
    service = job.service
    os_actor = service.aysrepo.actorGet('os.ssh.ubuntu')
    os_actor.serviceCreate(service.name, args={'node': service.name, 'sshkey': service.model.data.sshkey})

    users = service.model.data.uservdc
    for user in users:
        uservdc = service.aysrepo.serviceGet('uservdc', user.name)
        service.consume(uservdc)


def _authorization_user(machine, service, action=""):
    from JumpScale9Lib.clients.portal.PortalClient import ApiError

    users_list = service.producers.get('uservdc', [])
    if not users_list:
        return

    users = []
    for u in users_list:
        if u.model.data.provider != '':
            users.append(u.model.dbobj.name + "@" + u.model.data.provider)
        else:
            users.append(u.model.dbobj.name)
    try:
        machine_info = machine.client.api.cloudapi.machines.get(machineId=machine.id)
    except ApiError as err:
        service.logger.error(
            'Failed to retrieve machine information for machine {}. Error: {}'.format(machine.id, err)
        )
        raise
    # get acl info
    acl_info = {}
    for item in machine_info['acl']:
        acl_info[item['userGroupId']] = item

    # Authorize users
    for user in users:
        # user is not registered...then add it
        if user not in acl_info:
            if not action or action == 'add':
                for uvdc in service.model.data.uservdc:
                    if uvdc.name == user.split('@')[0]:
                        try:
                            result = machine.client.api.cloudapi.machines.addUser(
                                machineId=machine.id, userId=user, accesstype=uvdc.accesstype
                            )
                        except ApiError as err:
                            service.logger.error(
                                """
                                Failed to register access rights for user {} on machine {}.
                                Error: {}
                                """.format(user, machine.name, err)
                            )
                            raise
                        if result is not True:
                            service.logger.error(
                                'Failed to register access rights for user {} on machine {}'.format(user, machine.name)
                            )
            elif action == 'delete':
                service.logger.warning(
                    'User {} does not have access rights on machine {}'.format(user, machine.name)
                )
            else:
                # user is not registered while action is not add,
                # then we need to fail to prevent users from registering users by mistake
                msg = """
                User {} is not registered to have access rights on machine {}.
                If you want to register user, please use add_user action
                """.format(user, machine.name)
                service.logger.error(msg)
                raise RuntimeError(msg)

        else:
            # user already registered, check if the acl changed
            existing_acl = acl_info[user]['right']
            for uvdc in service.model.data.uservdc:
                if uvdc.name == user.split('@')[0]:
                    if not action or action == "update" or (action == "add" and existing_acl != uvdc.accesstype):
                        try:
                            result = machine.client.api.cloudapi.machines.updateUser(
                                machineId=machine.id, userId=user, accesstype=uvdc.accesstype
                            )
                        except ApiError as err:
                            service.logger.error(
                                """
                                Failed to update access rights for user {} on machine {}.
                                Error: {}""".format(user, machine.name, err)
                            )
                            raise
                        if result is not True:
                            service.logger.error(
                                'Failed to update access rights for user {} on machine {}'.format(user, machine.name)
                            )
                    elif action == 'delete':
                        try:
                            machine.client.api.cloudapi.machines.deleteUser(machineId=machine.id, userId=user)
                        except ApiError as err:
                            service.logger.error(
                                """
                                Failed to delete access rights for user {} on machine {}.
                                Error: {}""".format(user, machine.name, err)
                            )
                            raise
                    elif action == 'add' and existing_acl == uvdc.accesstype:
                        service.logger.info(
                            'User {} already have the required access type on machine {}'.format(user, machine.name)
                        )


def install(job):
    service = job.service
    space = _get_cloud_space(service)

    # Get machine if already exists or create a new one
    machine = space.machines.get(service.name)
    if not machine:
        machine = _create_machine(service, space)

    # Configure Ports including SSH port if not defined
    _configure_ports(service, machine)

    # register users acls
    _authorization_user(machine, service)

    # set machine id, ip, login data
    ip, vm_info = machine.get_machine_ip()
    if not ip:
        raise j.exceptions.RuntimeError('The machine %s does not get an IP ' % service.name)

    service.model.data.machineId = machine.id
    service.model.data.ipPublic = machine.space.model['publicipaddress'] or space.get_space_ip()
    service.model.data.ipPrivate = ip
    service.model.data.sshLogin = vm_info['accounts'][0]['login']
    service.model.data.sshPassword = vm_info['accounts'][0]['password']

    # Authorize ssh key into the machine
    prefab = _check_ssh_authorization(service, machine)

    # configure disks
    if prefab:
        _configure_disks(service, machine, prefab)

    # Save the service
    service.saveAll()


def processChange(job):
    # HERE we take care of changing ports and disks in the blueprints.
    #   ports:
    #       -REMOVING PORT FORWARDING IN BLUEPRINTS REFLECTS WILL REMOVE THE PORTFORWARD.
    #       -ADDING NEW PORT FORWARD IN BLUEPRINT WILL ADD A NEW PORTFORWARD.
    #       -EDITING PORT FOWARD IN BLUEPRINT = REMOVING THE OLD PORTFORWARD AND CREATING NEW ONE.
    #       -PORT 22 IS SPECIAL CASE WE KEEP IT EVEN IF EDITED OR DELETED.
    #   Disks:
    #       -add/delete data disk services = add/detach data disk to/from the machine.
    #       -delete boot disks will be ignored.
    service = job.service
    space = _get_cloud_space(service)

    if service.name in space.machines:
        # machine already exists
        machine = space.machines[service.name]
    else:
        raise RuntimeError('Machine {} was not found'.format(service.name))

    args = job.model.args
    category = args.pop('changeCategory')
    if category == "dataschema" and service.model.actionsState['install'] == 'ok':

        for key, value in args.items():
            if key == 'ports':

                old_pfs_set = set()
                new_pfs_set = set()
                old_ports = service.model.data.ports
                new_ports_list = value

                # HERE WE GET THE 22 mapping if exists
                for port in old_ports:
                    public_port, local_port = port.split(':')
                    old_pfs_set.add((public_port, local_port))

                if not isinstance(value, list):
                    raise j.exceptions.Input(message="Value is not a list.")

                for port in new_ports_list:
                    ss = port.split(':')
                    if len(ss) == 2:
                        public_port, local_port = ss
                    else:
                        local_port = port
                        public_port = None

                    new_pfs_set.add((public_port, local_port))

                to_remove = old_pfs_set - new_pfs_set
                to_create = new_pfs_set - old_pfs_set

                for public_port, local_port in to_remove:
                    if local_port == 22:
                        continue
                    machine.delete_portforwarding(public_port)

                for public_port, local_port in to_create:
                    machine.create_portforwarding(
                        publicport=public_port, localport=local_port, protocol='tcp'
                    )

                # Get all created ports forwarding to save it in the model
                all_ports = []
                for port_forward in machine.portforwardings:
                    port_added = "{public}:{local}".format(public=port_forward["publicPort"],
                                                           local=port_forward["localPort"])
                    all_ports.append(port_added)
                setattr(service.model.data, key, all_ports)

            if key == 'disk':
                # Get machine data disks only
                machine_disks = {disk['name']: disk['id'] for disk in machine.disks if disk['type'] != 'B'}
                old_disks_services = service.producers.get('disk', [])

                # Check for removed disk services which aren't of type B(boot), and delete them
                for old_disk_service in old_disks_services:
                    if old_disk_service.name not in value and old_disk_service.model.data.type != 'B':
                        service.model.producerRemove(old_disk_service)
                        device_name = old_disk_service.model.dbobj.name
                        if device_name in machine_disks:
                            machine.detach_disk(machine_disks[device_name])

                # Check for the new disk services and add them
                for disk_service_name in value:
                    disk_service = service.aysrepo.serviceGet('disk.ovc', disk_service_name)
                    if disk_service not in old_disks_services:
                        service.consume(disk_service)
                        disk_args = disk_service.model.data
                        disk_id = machine.add_disk(name=disk_service.name,
                                                   description=disk_args.description,
                                                   size=disk_args.size,
                                                   type=disk_args.type.upper(),
                                                   ssdSize=disk_args.ssdSize)
                        machine.disk_limit_io(disk_id, disk_args.maxIOPS)

                setattr(service.model.data, key, value)

            if key in ['cloneName', 'snapshotEpoch']:
                setattr(service.model.data, key, value)

        space.save()
        service.save()


def export(job):
    service = job.service
    vdc = service.parent
    if 'g8client' not in vdc.producers:
        raise j.exceptions.AYSNotFound("No producer g8client found. Cannot continue export of %s" % service)

    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)

    if service.name not in space.machines:
        raise j.exceptions.NotFound("Can not find a machine with this name %s" % service.name)
    cl.api.cloudapi.machines.exportOVF(
                    link=service.model.data.ovfLink,
                    username=service.model.data.ovfUsername,
                    passwd=service.model.data.ovfPassword,
                    path=service.model.data.ovfPath,
                    machineId=service.model.data.machineId,
                    callbackUrl=service.model.data.ovfCallbackUrl)


def import_(job):
    service = job.service
    space = _get_cloud_space(service)
    size_id = space.size_find_id(service.model.data.memory)
    service.client.api.cloudapi.machines.importOVF(
        link=service.model.data.ovfLink,
        username=service.model.data.ovfUsername,
        passwd=service.model.data.ovfPassword,
        path=service.model.data.ovfPath,
        cloudspaceId=space.id,
        name=service.name,
        sizeId=size_id,
        callbackUrl=service.model.data.ovfCallbackUrl
    )


def init_actions_(service, args):
    """
    this needs to returns an array of actions representing the dependencies between actions.
    Looks at ACTION_DEPS in this module for an example of what is expected
    """
    # some default logic for simple actions

    action_required = args.get('action_required')

    if action_required in ['stop', 'uninstall']:
        for action_name, action_model in service.model.actions.items():
            if action_name in ['stop', 'uninstall']:
                continue
            if action_model.state == 'scheduled':
                action_model.state = 'new'

    if action_required in ['install']:
        for action_name, action_model in service.model.actions.items():
            if action_name in ['uninstall', 'stop'] and action_model.state == 'scheduled':
                action_model.state = 'new'

    if action_required == 'stop':
        if service.model.actionsState['start'] == 'sheduled':
            service.model.actionsState['start'] = 'new'

    if action_required == 'start':
        if service.model.actionsState['stop'] == 'sheduled':
            service.model.actionsState['stop'] = 'new'

    service.save()

    return {
        'init': [],
        'install': ['init'],
        'start': ['install'],
        'export': ['install'],
        'import_': ['init'],
        'monitor': ['start'],
        'stop': ['install'],
        'clone': ['install', 'stop'],
        'get_history': ['install'],
        'attach_external_network': ['install'],
        'detach_external_network': ['install'],
        'uninstall': ['stop'],
        'add_user': ['install'],
        'update_user': ['install'],
        'delete_user': ['install'],
        'pause': ['install'],
        'resume': ['install'],
        'restart': ['install'],
        'list_snapshots': ['install'],
        'snapshot': ['install'],
        'rollback_snapshot': ['install', 'stop'],
        'delete_snapshot': ['install']
    }


def add_disk(job):
    service = job.service
    repo = service.aysrepo
    space = _get_cloud_space(service)

    # find os
    os = None
    for child in service.children:
        if child.model.role == 'os':
            os = child
            break

    if os is None:
        raise RuntimeError('no child os found')

    if service.name in space.machines:
        # machine already exists
        machine = space.machines[service.name]
    else:
        raise RuntimeError('Machine {} was not found'.format(service.name))

    args = job.model.args
    prefix = args.get('prefix', 'added')

    available_disks = service.producers.get('disk', [])
    available_names = service.model.data.disk
    device_names = list(map(lambda d: d.model.data.devicename, available_disks))
    idx = 1
    name = '%s-%d' % (prefix, idx)
    while name in available_names:
        idx += 1
        name = '%s-%d' % (prefix, idx)

    model = {
        'size': args.get('size', 1000),
        'description': args.get('description', 'disk'),
    }

    machine.add_disk(name=name, description=model['description'], size=model['size'], type='D')

    code, out, err = os.executor.prefab.core.run("lsblk -J", die=False)
    if code != 0:
        raise RuntimeError('failed to list devices on node: %s' % err)

    jsonout = j.data.serializer.json.loads(out)
    # should be only 1
    devices = [x for x in jsonout['blockdevices'] if x['mountpoint'] is None and x['type'] == 'disk']

    for dv in devices:
        if 'children' in dv or dv['name'] in device_names:
            continue
        model['devicename'] = dv['name']

    disk_service = repo.actorGet('disk.ovc').serviceCreate(name, model)
    disk_service.saveAll()
    service.consume(disk_service)
    disks = list(service.model.data.disk)
    disks.append(name)
    service.model.data.disk = disks
    service.saveAll()


def open_port(job):
    """
    Open port in the firewall by creating port forward
    if public_port is None, auto select available port
    Return the public port assigned
    """
    requested_port = job.model.args['requested_port']
    public_port = job.model.args.get('public_port', None)

    service = job.service
    space = _get_cloud_space(service)

    if service.name in space.machines:
        # machine already exists
        machine = space.machines[service.name]
    else:
        raise RuntimeError('machine not found')

    # check if already open, if yes return public port
    spaceport = None
    for pf in machine.portforwardings:
        if pf['localPort'] == requested_port:
            spaceport = pf['publicPort']
            break

    ports = set(service.model.data.ports)

    if spaceport is None:
        if public_port is None:
            # reach that point, the port is not forwarded yet
            unavailable_ports = [int(portinfo['publicPort']) for portinfo in machine.space.portforwardings]
            spaceport = 2200
            while True:
                if spaceport not in unavailable_ports:
                    break
                else:
                    spaceport += 1
        else:
            spaceport = public_port

        machine.create_portforwarding(spaceport, requested_port)

    ports.add("%s:%s" % (spaceport, requested_port))
    service.model.data.ports = list(ports)

    service.saveAll()

    return spaceport


def uninstall(job):
    service = job.service
    space = _get_cloud_space(service)
    if service.name not in space.machines:
        service.logger.warning("Machine doesn't exist in the cloud space")
        return
    machine = space.machines[service.name]
    machine.delete()


def start(job):
    space = _get_cloud_space(job.service)
    machine = space.machines[job.service.name]
    _check_ssh_authorization(job.service, machine)
    machine.start()


def stop(job):
    space = _get_cloud_space(job.service)
    machine = space.machines[job.service.name]
    _check_ssh_authorization(job.service, machine)
    machine.stop()


def restart(job):
    space = _get_cloud_space(job.service)
    machine = space.machines[job.service.name]
    _check_ssh_authorization(job.service, machine)
    machine.restart()


def pause(job):
    space = _get_cloud_space(job.service)
    machine = space.machines[job.service.name]
    _check_ssh_authorization(job.service, machine)
    machine.pause()


def resume(job):
    space = _get_cloud_space(job.service)
    machine = space.machines[job.service.name]
    _check_ssh_authorization(job.service, machine)
    machine.resume()


def reset(job):
    space = _get_cloud_space(job.service)
    machine = space.machines[job.service.name]
    _check_ssh_authorization(job.service, machine)
    machine.reset()


def clone(job):
    """
    Action that creates a clone of a machine.
    """
    service = job.service
    vdc = service.parent

    if 'g8client' not in vdc.producers:
        raise j.exceptions.RuntimeError("No producer g8client found. Cannot continue clone of %s" % service)

    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)

    if service.name not in space.machines:
        raise j.exceptions.RuntimeError("Machine with name %s doesn't exist in the cloud space" % service.name)

    machine = space.machines[service.name]

    clone_name = service.model.data.cloneName

    machine.clone(clone_name)
    machine.start()


def get_history(job):
    import json
    service = job.service
    space = _get_cloud_space(service)
    machine = space.machines[service.name]
    _check_ssh_authorization(job.service, machine)
    res = machine.getHistory(10)
    service.model.data.vmHistory = json.dumps(res)
    service.saveAll()


def attach_external_network(job):
    """
    Action that attaches the machine to the external network.
    """
    service = job.service
    vdc = service.parent

    if 'g8client' not in vdc.producers:
        raise j.exceptions.RuntimeError("No producer g8client found. Cannot continue attaching external network to %s" % service)

    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)

    if service.name not in space.machines:
        raise j.exceptions.RuntimeError("Machine with name %s doesn't exist in the cloud space" % service.name)

    machine = space.machines[service.name]
    machine.attach_external_network()

def detach_external_network(job):
    """
    Action that detaches the machine from the external network.
    """
    service = job.service
    vdc = service.parent

    if 'g8client' not in vdc.producers:
        raise j.exceptions.RuntimeError("No producer g8client found. Cannot continue detaching external network from %s" % service)

    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)

    if service.name not in space.machines:
        raise j.exceptions.RuntimeError("Machine with name %s doesn't exist in the cloud space" % service.name)

    machine = space.machines[service.name]
    machine.detach_external_network()


def mail(job):
    print('hello world')


def _update_user_acl(job, action):
    """
    Updates user access rights on the machine
    """
    service = job.service
    vdc = service.parent

    if 'g8client' not in vdc.producers:
        raise j.exceptions.RuntimeError("No producer g8client found. Cannot continue reset of %s" % service)
    g8client = vdc.producers["g8client"][0]

    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)

    if service.name not in space.machines:
        msg = "Machine {} doesn't exist in the cloud space {}".format(service.name, space.name)
        service.logger.warning(msg)
        raise RuntimeError(msg)
    machine = space.machines[service.name]
    _authorization_user(machine, service, action=action)
    service.saveAll()


def add_user(job):
    """
    Give a registered user access rights to the machine
    """
    _update_user_acl(job=job, action='add')


def update_user(job):
    """
    Update a registered user access rights to the machine
    """
    _update_user_acl(job=job, action='update')


def delete_user(job):
    """
    Remove a registered user access rights to the machine
    """
    _update_user_acl(job=job, action='delete')


def list_snapshots(job):
    """
    Action that lists the snapshots of the machine
    """
    import json
    service = job.service
    vdc = service.parent

    if 'g8client' not in vdc.producers:
        raise j.exceptions.RuntimeError("No producer g8client found. Cannot continue creating snapshot of %s" % service)

    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)

    if service.name not in space.machines:
        raise j.exceptions.RuntimeError("Machine with name %s doesn't exist in the cloud space" % service.name)

    machine = space.machines[service.name]
    res = machine.list_snapshots()
    service.model.data.snapshots = [json.dumps(s) for s in res]

    service.saveAll()


def snapshot(job):
    """
    Action that creates a snapshot of the machine
    """
    service = job.service
    vdc = service.parent

    if 'g8client' not in vdc.producers:
        raise j.exceptions.RuntimeError("No producer g8client found. Cannot continue creating snapshot of %s" % service)

    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)

    if service.name not in space.machines:
        raise j.exceptions.RuntimeError("Machine with name %s doesn't exist in the cloud space" % service.name)

    machine = space.machines[service.name]
    machine.create_snapshot(machine.name)


def rollback_snapshot(job):
    """
    Action that rolls back the machine to a snapshot
    """
    service = job.service
    vdc = service.parent

    if 'g8client' not in vdc.producers:
        raise j.exceptions.RuntimeError("No producer g8client found. Cannot continue creating snapshot of %s" % service)

    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)

    if service.name not in space.machines:
        raise j.exceptions.RuntimeError("Machine with name %s doesn't exist in the cloud space" % service.name)

    machine = space.machines[service.name]
    snapshot_epoch = service.model.data.snapshotEpoch

    machine.rollback_snapshot(snapshot_epoch)
    machine.start()


def delete_snapshot(job):
    """
    Action that deletes a snapshot of the machine
    """
    service = job.service
    vdc = service.parent

    if 'g8client' not in vdc.producers:
        raise j.exceptions.RuntimeError("No producer g8client found. Cannot continue creating snapshot of %s" % service)

    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)

    if service.name not in space.machines:
        raise j.exceptions.RuntimeError("Machine with name %s doesn't exist in the cloud space" % service.name)

    machine = space.machines[service.name]
    snapshot_epoch = service.model.data.snapshotEpoch

    machine.delete_snapshot(snapshot_epoch)

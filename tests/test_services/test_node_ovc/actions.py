def init_actions_(service, args):
    return {
        'test_create': ['install'],
        'test_delete': ['install'],
        'test_attach_external_network': ['attach_external_network'],
        'test_detach_external_network': ['detach_external_network'],
        'test_clone': ['clone'],
        'test_snapshot': ['snapshot'],
        'test_list_snapshots': ['list_snapshots'],
        'test_delete_snapshot': ['delete_snapshot']
    }

#################
# dummy functions to make the tests depend on the actions in node.ovc
def attach_external_network(job):
    pass

def detach_external_network(job):
    pass

def clone(job):
    pass

def snapshot(job):
    pass

def list_snapshots(job):
    pass

def delete_snapshot(job):
    pass
#################

def test_create(job):
    import sys
    RESULT_OK = 'OK : %s '
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s'

    service = job.service
    try:
        g8client = service.producers['g8client'][0]
        client = j.clients.openvcloud.getFromService(g8client)

        vm = service.producers['node'][0]
        vm_id = vm.model.data.machineId

        machine = client.api.cloudapi.machines.get(machineId=vm_id)

        if vm.name != machine['name']:
            failure = vm.name + '!=' + machine['name']
            service.model.data.result = RESULT_FAILED % failure
        elif vm.model.data.osImage != machine['osImage']:
            failure = service.model.data.osImage + '!=' + machine['osImage']
            service.model.data.result = RESULT_FAILED % failure
        elif vm.model.data.bootdiskSize != machine['disks'][0]['sizeMax']:
            failure = service.model.data.bootdiskSize + '!=' + machine['disks'][0]['sizeMax']
            service.model.data.result = RESULT_FAILED % failure
        else:
            service.model.data.result = RESULT_OK % 'test_create_virtualmachine'

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()


def test_delete(job):
    import sys
    RESULT_OK = 'OK : %s '
    RESULT_ERROR = 'ERROR : %s'

    service = job.service
    try:
        g8client = service.producers['g8client'][0]
        client = j.clients.openvcloud.getFromService(g8client)

        vm = service.producers['node'][0]
        vm_name = vm.name
        vdc = service.producers['vdc'][0]
        vdc_id = vdc.model.data.cloudspaceID

        machines = client.api.cloudapi.machines.list(cloudspaceId=vdc_id)

        if any(vm['name'] == vm_name for vm in machines):
            failure = 'vm is not deleted'
            service.model.data.result = RESULT_FAILED % failure
        else:
            service.model.data.result = RESULT_OK % 'test_delete_virtualmachine'

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()


def test_node_disks(job):
    import sys
    RESULT_OK = 'OK : %s '
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s'

    service = job.service
    try:
        g8client = service.producers['g8client'][0]
        client = j.clients.openvcloud.getFromService(g8client)

        vm = service.producers['node'][0]
        vm_id = vm.model.data.machineId

        machine = client.api.cloudapi.machines.get(machineId=vm_id)

        disks = vm.producers.get('disk', [])
        # length of service disks +1(boot disk) should equal the actual number of machine disks
        if (len(disks) + 1) != len(machine['disks']):
            failure = 'Machine Model Disks({}) != Actual Machine Disks({})'.format(len(disks)+1, len(machine['disks']))
            service.model.data.result = RESULT_FAILED % failure
        else:
            service.model.data.result = RESULT_OK % 'test_node_disks'

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()


def test_attach_external_network(job):
    import sys
    RESULT_OK = 'OK : %s '
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s'

    service = job.service
    try:
        g8client = service.producers['g8client'][0]
        client = j.clients.openvcloud.getFromService(g8client)

        vm = service.producers['node'][0]
        vm_id = vm.model.data.machineId

        machine = client.api.cloudapi.machines.get(machineId=vm_id)

        # check if machine is attached: there should be an interface with type PUBLIC
        if not any(inter['type'] == 'PUBLIC' for inter in machine['interfaces']):
            failure = 'Machine is not attached to external network '
            service.model.data.result = RESULT_FAILED % failure
        else:
            service.model.data.result = RESULT_OK % 'test_attach_external_network'

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()


def test_detach_external_network(job):
    import sys
    RESULT_OK = 'OK : %s '
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s'

    service = job.service
    try:
        g8client = service.producers['g8client'][0]
        client = j.clients.openvcloud.getFromService(g8client)

        vm = service.producers['node'][0]
        vm_id = vm.model.data.machineId

        machine = client.api.cloudapi.machines.get(machineId=vm_id)

        # check if machine is detached: there should not be an interface with type PUBLIC
        if any(inter['type'] == 'PUBLIC' for inter in machine['interfaces']):
            failure = 'Machine is not detached from external network '
            service.model.data.result = RESULT_FAILED % failure
        else:
            service.model.data.result = RESULT_OK % 'test_detach_external_network'

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()


def test_clone(job):
    import sys
    RESULT_OK = 'OK : %s '
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s'

    service = job.service
    try:
        g8client = service.producers['g8client'][0]
        client = j.clients.openvcloud.getFromService(g8client)

        vm = service.producers['node'][0]
        vm_id = vm.model.data.machineId
        vdc = service.producers['vdc'][0]
        vdc_id = vdc.model.data.cloudspaceID

        machines = client.api.cloudapi.machines.list(cloudspaceId=vdc_id)

        clone_name = 'testnode_clone'

        res = [machine['id'] for machine in machines if machine['name'] == clone_name]
        if res:
            # get id of cloned vm
            clone_id = res[0]
            machine = client.api.cloudapi.machines.get(machineId=clone_id)

            # check if this vm is a clone of the original vm
            if clone_name != machine['name']:
                failure = vm.name + '!=' + machine['name']
                service.model.data.result = RESULT_FAILED % failure
            elif vm.model.data.osImage != machine['osImage']:
                failure = service.model.data.osImage + '!=' + machine['osImage']
                service.model.data.result = RESULT_FAILED % failure
            elif vm.model.data.bootdiskSize != machine['disks'][0]['sizeMax']:
                failure = service.model.data.bootdiskSize + '!=' + machine['disks'][0]['sizeMax']
                service.model.data.result = RESULT_FAILED % failure
            else:
                service.model.data.result = RESULT_OK % 'test_clone_machine'
        else:
            failure = 'clone of %s is not created' % vm.name
            service.model.data.result = RESULT_FAILED % failure

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()


def test_snapshot(job):
    import sys
    RESULT_OK = 'OK : %s '
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s'

    service = job.service
    try:
        g8client = service.producers['g8client'][0]
        client = j.clients.openvcloud.getFromService(g8client)

        vm = service.producers['node'][0]
        vm_id = vm.model.data.machineId

        content = client.api.cloudapi.machines.listSnapshots(machineId=vm_id)

        # check if list of snapshots is not empty
        if not content:
            failure = 'Snapshot is not created'
            service.model.data.result = RESULT_FAILED % failure
        else:
            service.model.data.result = RESULT_OK % 'test_snapshot'

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()


def test_list_snapshots(job):
    import sys
    import json
    RESULT_OK = 'OK : %s '
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s'

    service = job.service
    try:
        g8client = service.producers['g8client'][0]
        client = j.clients.openvcloud.getFromService(g8client)

        vm = service.producers['node'][0]
        vm_id = vm.model.data.machineId

        content = client.api.cloudapi.machines.listSnapshots(machineId=vm_id)

        # check if snapshot lists match
        if content != vm.model.data.snapshots:
            failure = 'Snapshots are not listed correctly'
            service.model.data.result = RESULT_FAILED % failure
        else:
            service.model.data.result = RESULT_OK % 'test_list_snapshots'
            # prepare test_delete_snapshot: set epoch of snapshot
            vm['data']['snapshotEpoch'] = content[0]['epoch']

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()


def test_delete_snapshot(job):
    import sys
    RESULT_OK = 'OK : %s '
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s'

    service = job.service
    try:
        g8client = service.producers['g8client'][0]
        client = j.clients.openvcloud.getFromService(g8client)

        vm = service.producers['node'][0]
        vm_id = vm.model.data.machineId

        content = client.api.cloudapi.machines.listSnapshots(machineId=vm_id)

        # check if list of snapshots is empty
        if content:
            failure = 'Snapshot is not deleted'
            service.model.data.result = RESULT_FAILED % failure
        else:
            service.model.data.result = RESULT_OK % 'test_delete_snapshot'

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()

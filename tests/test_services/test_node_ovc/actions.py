def init_actions_(service, args):
    return {
        'test_create': ['install'],
        'test_delete': ['install'],
        'test_attach_external_network': ['attach_external_network'],
        'test_detach_external_network': ['detach_external_network'],
        'test_clone': ['clone']
    }


##############
# dummy methods for making tests depend on the actions they test
def attach_external_network(job):
    pass

def detach_external_network(job):
    pass

def clone(job):
    pass
##############

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

        content = client.api.cloudapi.machines.get(machineId=vm_id)

        if vm.name != content['name']:
            failure = vm.name + '!=' + content['name']
            service.model.data.result = RESULT_FAILED % failure
        elif vm.model.data.osImage != content['osImage']:
            failure = service.model.data.osImage + '!=' + content['osImage']
            service.model.data.result = RESULT_FAILED % failure
        elif vm.model.data.bootdiskSize != content['disks'][0]['sizeMax']:
            failure = service.model.data.bootdiskSize + '!=' + content['disks'][0]['sizeMax']
            service.model.data.result = RESULT_FAILED % failure
        else:
            service.model.data.result = RESULT_OK % 'test_create_virtualmachine'

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()


def test_delete(job):
    import requests
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

        content = client.api.cloudapi.machines.list(cloudspaceId=vdc_id)

        if any(vm['name'] == vm_name for vm in content):
            failure = 'vm is not deleted'
            service.model.data.result = RESULT_FAILED % failure
        else:
            service.model.data.result = RESULT_OK % 'test_delete_virtualmachine'

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()


def test_node_disks(job):
    import requests
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

        content = client.api.cloudapi.machines.get(machineId=vm_id)

        disks = vm.producers.get('disk', [])
        # length of service disks +1(boot disk) should equal the actual number of machine disks
        if (len(disks) + 1) != len(content['disks']):
            failure = 'Machine Model Disks({}) != Actual Machine Disks({})'.format(len(disks)+1, len(content['disks']))
            service.model.data.result = RESULT_FAILED % failure
        else:
            service.model.data.result = RESULT_OK % 'test_node_disks'

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()


def test_attach_external_network(job):
    import requests
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

        content = client.api.cloudapi.machines.get(machineId=vm_id)

        # check if machine is attached: there should be an interface with type PUBLIC
        if not any(inter['type'] == 'PUBLIC' for inter in content['interfaces']):
            failure = 'Machine is not attached to external network '
            service.model.data.result = RESULT_FAILED % failure
        else:
            service.model.data.result = RESULT_OK % 'test_attach_external_network'

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()


def test_detach_external_network(job):
    import requests
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

        content = client.api.cloudapi.machines.get(machineId=vm_id)

        # check if machine is detached: there should not be an interface with type PUBLIC
        if any(inter['type'] == 'PUBLIC' for inter in content['interfaces']):
            failure = 'Machine is not detached from external network '
            service.model.data.result = RESULT_FAILED % failure
        else:
            service.model.data.result = RESULT_OK % 'test_detach_external_network'

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()


def test_clone(job):
    import requests
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

        content = client.api.cloudapi.machines.list(cloudspaceId=vdc_id)

        clone_name = "%s_clone" % vm.name

        res = [machine['id'] for machine in content if machine['name'] == clone_name]
        if res:
            # get id of cloned vm
            clone_id = res[0]
            content = client.api.cloudapi.machines.get(machineId=clone_id)

            # check if this vm is a clone of the original vm
            if clone_name != content['name']:
                failure = vm.name + '!=' + content['name']
                service.model.data.result = RESULT_FAILED % failure
            elif vm.model.data.osImage != content['osImage']:
                failure = service.model.data.osImage + '!=' + content['osImage']
                service.model.data.result = RESULT_FAILED % failure
            elif vm.model.data.bootdiskSize != content['disks'][0]['sizeMax']:
                failure = service.model.data.bootdiskSize + '!=' + content['disks'][0]['sizeMax']
                service.model.data.result = RESULT_FAILED % failure
            else:
                service.model.data.result = RESULT_OK % 'test_clone_machine'
        else:
            failure = 'clone of %s is not created' % vm.name
            service.model.data.result = RESULT_FAILED % failure

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()

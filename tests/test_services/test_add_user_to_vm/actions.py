def test_user_access(job):
    import requests, sys, time
    service = job.service
    RESULT_OK = 'OK : %s ' % service.name
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s'
    failures = []
    try:
        service.model.data.result = RESULT_OK
        openv_client = j.clients.openvcloud.getFromService(service.producers.get('g8client')[0])
        node_srv = service.producers.get('node')[0]
        vdc_srv = node_srv.producers.get('vdc')[0]
        for vdc in openv_client.api.cloudapi.cloudspaces.list():
            if vdc['name'] == vdc_srv.name:
                break
        if vdc['name'] != vdc_srv.name:
            raise RuntimeError('No matching cloudspace found')
        
        for vm in openv_client.api.cloudapi.machines.list(cloudspaceId=vdc['id']):
            if vm['name'] == node_srv.name:
                break
        if vm['name'] != node_srv.name:
            raise RuntimeError('No matching VM found')

        machine_info = openv_client.api.cloudapi.machines.get(machineId=vm['id'])
        configured_uservdc = node_srv.model.data.uservdc[0]
        acls = machine_info['acl']
        for acl in acls:
            if acl['userGroupId'] == configured_uservdc.name:
                if acl['right'] != configured_uservdc.accesstype:
                    service.model.data.result = RESULT_FAILED %\
                             ('User is not confgured correctly: Expected acl: [%s] Found acl: [%s]' % (configured_uservdc.accesstype, acl['right']))
    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    finally:
        service.save()


def test_delete_user_access(job):
    import requests, sys, time
    service = job.service
    RESULT_OK = 'OK : %s ' % service.name
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s'
    failures = []
    try:
        service.model.data.result = RESULT_OK
        openv_client = j.clients.openvcloud.getFromService(service.producers.get('g8client')[0])
        node_srv = service.producers.get('node')[0]
        vdc_srv = node_srv.producers.get('vdc')[0]
        for vdc in openv_client.api.cloudapi.cloudspaces.list():
            if vdc['name'] == vdc_srv.name:
                break
        if vdc['name'] != vdc_srv.name:
            raise RuntimeError('No matching cloudspace found')

        for vm in openv_client.api.cloudapi.machines.list(cloudspaceId=vdc['id']):
            if vm['name'] == node_srv.name:
                break
        if vm['name'] != node_srv.name:
            raise RuntimeError('No matching VM found')

        machine_info = openv_client.api.cloudapi.machines.get(machineId=vm['id'])
        # after deleting the all the users access rights, only the owner of machine should have access right
        if len(machine_info['acl']) > 1:
            service.model.data.result = RESULT_FAILED % 'Unconfigured users have access to machine [%s]' % machine_info['name'] 
    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    finally:
        service.save()

def init_actions_(service, args):
    return {
        'test_create': ['install'],
        'test_delete': ['install'],
        'test_enable': ['enable'],
        'test_disable': ['disable'],
    }

##############
# dummy methods for making tests depend on the actions they test
def enable(job):
    pass

def disable(job):
    pass
##############

def test_create(job):
    import requests
    import sys
    RESULT_OK = 'OK : %s '
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s'

    service = job.service
    try:
        g8client = service.producers['g8client'][0]
        client = j.clients.openvcloud.getFromService(g8client)

        vdc = service.producers['vdc'][0]
        vdc_id = vdc.model.data.cloudspaceID

        content = client.api.cloudapi.cloudspaces.get(cloudspaceId=vdc_id)

        if vdc.name != content['name']:
            failure = vdc.name + '!=' + content['name']
            service.model.data.result = RESULT_FAILED % failure
        else:
            service.model.data.result = RESULT_OK % 'test_create_vdc'

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()


def test_delete(job):
    import requests
    import sys
    RESULT_OK = 'OK : %s '
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s'

    service = job.service
    try:
        g8client = service.producers['g8client'][0]
        client = j.clients.openvcloud.getFromService(g8client)

        vdc = service.producers['vdc'][0]
        vdc_id = vdc.model.data.cloudspaceID

        content = client.api.cloudapi.cloudspaces.get(cloudspaceId=vdc_id)

        if content['status'] != 'DESTROYED':
            failed = 'Cloudspace was not deleted'
            service.model.data.result = RESULT_FAILED % failed
        else:
            service.model.data.result = RESULT_OK % 'test_delete_vdc'

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()

def test_enable(job):
    import requests
    import sys
    RESULT_OK = 'OK : %s '
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s'

    service = job.service
    try:
        g8client = service.producers['g8client'][0]
        client = j.clients.openvcloud.getFromService(g8client)

        vdc = service.producers['vdc'][0]
        vdc_id = vdc.model.data.cloudspaceID

        content = client.api.cloudapi.cloudspaces.get(cloudspaceId=vdc_id)

        # check if vdc is enabled
        if content['status'] != 'DEPLOYED':
            failure = 'vdc is not deployed'
            service.model.data.result = RESULT_FAILED % failure
        else:
            service.model.data.result = RESULT_OK % 'test_enable_vdc'

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()

def test_disable(job):
    import requests
    import sys
    RESULT_OK = 'OK : %s '
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s'

    service = job.service
    try:
        g8client = service.producers['g8client'][0]
        client = j.clients.openvcloud.getFromService(g8client)

        vdc = service.producers['vdc'][0]
        vdc_id = vdc.model.data.cloudspaceID

        content = client.api.cloudapi.cloudspaces.get(cloudspaceId=vdc_id)

        # check if vdc is disabled
        if content['status'] != 'DISABLED':
            failure = 'vdc is not disabled'
            service.model.data.result = RESULT_FAILED % failure
        else:
            service.model.data.result = RESULT_OK % 'test_disable_vdc'

    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()

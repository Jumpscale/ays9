def init_actions_(service, args):
    return {
        'test_create': ['init'],
        'test_disable': ['init'],
        'test_enable': ['init'],
        'test_delete': ['init'],
    }


def test_create(job):
    import requests
    import sys
    RESULT_OK = 'OK : %s '
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s'

    service = job.service
    try:
        g8client = service.producers['g8client'][0]
        url = 'https://' + g8client.model.data.url
        username = g8client.model.data.login
        password = g8client.model.data.password
        login_url = url + '/restmachine/system/usermanager/authenticate'
        credential = {'name': username,
                      'secret': password}
        session = requests.Session()
        session.post(url=login_url, data=credential)

        vdc = service.producers['vdc'][0]
        vdc_id = vdc.model.data.cloudspaceID

        api_url = url + '/restmachine/cloudapi/cloudspaces/get'
        api_body = {'cloudspaceId': vdc_id}

        response = session.post(url=api_url, data=api_body)

        if response.status_code == 200:
            content = response.json()
            if vdc.name != content['name']:
                failure = vdc.name + '!=' + content['name']
                service.model.data.result = RESULT_FAILED % failure
            else:
                service.model.data.result = RESULT_OK % 'test_create_vdc'
        else:
            response_data = {'status_code': response.status_code,
                             'content': response.content}
            service.model.data.result = RESULT_ERROR % str(response_data)+str(vdc_id)
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
        url = 'https://' + g8client.model.data.url
        username = g8client.model.data.login
        password = g8client.model.data.password
        login_url = url + '/restmachine/system/usermanager/authenticate'
        credential = {'name': username,
                      'secret': password}
        session = requests.Session()
        session.post(url=login_url, data=credential)

        vdc = service.producers['vdc'][0]
        vdc_id = vdc.model.data.cloudspaceID

        api_url = url + '/restmachine/cloudapi/cloudspaces/delete'
        api_body = {'cloudspaceId': vdc_id}

        response = session.post(url=api_url, data=api_body)

        if response.status_code == 404:
            service.model.data.result = RESULT_OK % 'test_delete_vdc'
        else:
            response_data = {'status_code': response.status_code,
                             'content': response.content}
            service.model.data.result = RESULT_ERROR % str(response_data)+str(vdc_id)
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
        url = 'https://' + g8client.model.data.url
        username = g8client.model.data.login
        password = g8client.model.data.password
        login_url = url + '/restmachine/system/usermanager/authenticate'
        credential = {'name': username,
                      'secret': password}
        session = requests.Session()
        session.post(url=login_url, data=credential)

        vdc = service.producers['vdc'][0]
        vdc_id = vdc.model.data.cloudspaceID

        api_url = url + '/restmachine/cloudapi/cloudspaces/get'
        api_body = {'cloudspaceId': vdc_id}

        response = session.post(url=api_url, data=api_body)

        if response.status_code == 200:
            content = response.json()
            # check if vdc is enabled
            if content['status'] != 'DEPLOYED':
                failure = 'vdc is not deployed'
                service.model.data.result = RESULT_FAILED % failure
            else:
                service.model.data.result = RESULT_OK % 'test_enable_vdc'
        else:
            response_data = {'status_code': response.status_code,
                             'content': response.content}
            service.model.data.result = RESULT_ERROR % str(response_data)+str(vdc_id)
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
        url = 'https://' + g8client.model.data.url
        username = g8client.model.data.login
        password = g8client.model.data.password
        login_url = url + '/restmachine/system/usermanager/authenticate'
        credential = {'name': username,
                      'secret': password}
        session = requests.Session()
        session.post(url=login_url, data=credential)

        vdc = service.producers['vdc'][0]
        vdc_id = vdc.model.data.cloudspaceID

        api_url = url + '/restmachine/cloudapi/cloudspaces/get'
        api_body = {'cloudspaceId': vdc_id}

        response = session.post(url=api_url, data=api_body)

        if response.status_code == 200:
            content = response.json()
            # check if vdc is disabled
            if content['status'] != 'DISABLED':
                failure = 'vdc is not disabled'
                service.model.data.result = RESULT_FAILED % failure
            else:
                service.model.data.result = RESULT_OK % 'test_disable_vdc'
        else:
            response_data = {'status_code': response.status_code,
                             'content': response.content}
            service.model.data.result = RESULT_ERROR % str(response_data)+str(vdc_id)
    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()

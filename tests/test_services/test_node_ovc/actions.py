def init_actions_(service, args):
    return {
        'test_create': ['init'],
        'test_delete': ['init'],
        'test_attach_external_network': ['init'],
        'test_detach_external_network': ['init'],
        'test_clone': ['init'],
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

        vm = service.producers['node'][0]
        vm_id = vm.model.data.machineId

        api_url = url + '/restmachine/cloudapi/machines/get'
        api_body = {'machineId': vm_id}

        response = session.post(url=api_url, data=api_body)

        if response.status_code == 200:
            content = response.json()
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
        else:
            response_data = {'status_code': response.status_code,
                             'content': response.content}
            service.model.data.result = RESULT_ERROR % str(response_data)+str(vm_id)
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

        vm = service.producers['node'][0]
        vm_id = vm.model.data.machineId

        api_url = url + '/restmachine/cloudapi/machines/get'
        api_body = {'machineId': vm_id}

        response = session.post(url=api_url, data=api_body)

        if response.status_code == 404:
            service.model.data.result = RESULT_OK % 'test_delete_virtualmachine'
        else:
            response_data = {'status_code': response.status_code,
                             'content': response.content}
            service.model.data.result = RESULT_ERROR % str(response_data)+str(vm_id)
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
        url = 'https://' + g8client.model.data.url
        username = g8client.model.data.login
        password = g8client.model.data.password
        login_url = url + '/restmachine/system/usermanager/authenticate'
        credential = {'name': username,
                      'secret': password}
        session = requests.Session()
        session.post(url=login_url, data=credential)

        vm = service.producers['node'][0]
        vm_id = vm.model.data.machineId

        api_url = url + '/restmachine/cloudapi/machines/get'
        api_body = {'machineId': vm_id}

        response = session.post(url=api_url, data=api_body)
        if response.status_code == 200:
            content = response.json()
            disks = vm.producers.get('disk', [])
            # length of service disks +1(boot disk) should equal the actual number of machine disks
            if (len(disks) + 1) != len(content['disks']):
                failure = 'Machine Model Disks({}) != Actual Machine Disks({})'.format(len(disks)+1, len(content['disks']))
                service.model.data.result = RESULT_FAILED % failure
            else:
                service.model.data.result = RESULT_OK % 'test_node_disks'
        else:
            response_data = {'status_code': response.status_code,
                             'content': response.content}
            service.model.data.result = RESULT_ERROR % str(response_data)+str(vm_id)
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
        url = 'https://' + g8client.model.data.url
        username = g8client.model.data.login
        password = g8client.model.data.password
        login_url = url + '/restmachine/system/usermanager/authenticate'
        credential = {'name': username,
                      'secret': password}
        session = requests.Session()
        session.post(url=login_url, data=credential)

        vm = service.producers['node'][0]
        vm_id = vm.model.data.machineId

        api_url = url + '/restmachine/cloudapi/machines/get'
        api_body = {'machineId': vm_id}

        response = session.post(url=api_url, data=api_body)

        if response.status_code == 200:
            content = response.json()
            # check if machine is attached: there should be an interface with type PUBLIC
            if not any(inter['type'] == 'PUBLIC' for inter in content['interfaces']):
                failure = 'Machine is not attached to external network '
                service.model.data.result = RESULT_FAILED % failure
            else:
                service.model.data.result = RESULT_OK % 'test_attach_external_network'
        else:
            response_data = {'status_code': response.status_code,
                             'content': response.content}
            service.model.data.result = RESULT_ERROR % str(response_data)+str(vm_id)
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
        url = 'https://' + g8client.model.data.url
        username = g8client.model.data.login
        password = g8client.model.data.password
        login_url = url + '/restmachine/system/usermanager/authenticate'
        credential = {'name': username,
                      'secret': password}
        session = requests.Session()
        session.post(url=login_url, data=credential)

        vm = service.producers['node'][0]
        vm_id = vm.model.data.machineId

        api_url = url + '/restmachine/cloudapi/machines/get'
        api_body = {'machineId': vm_id}

        response = session.post(url=api_url, data=api_body)

        if response.status_code == 200:
            content = response.json()
            # check if machine is detached: there should not be an interface with type PUBLIC
            if any(inter['type'] == 'PUBLIC' for inter in content['interfaces']):
                failure = 'Machine is not detached from external network '
                service.model.data.result = RESULT_FAILED % failure
            else:
                service.model.data.result = RESULT_OK % 'test_detach_external_network'
        else:
            response_data = {'status_code': response.status_code,
                             'content': response.content}
            service.model.data.result = RESULT_ERROR % str(response_data)+str(vm_id)
    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()


def test_clone(job):
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

        vm = service.producers['node'][0]

        api_url = url + '/restmachine/cloudapi/machines/list'
        response = session.post(url=api_url, data=None)

        clone_name = "%s_clone" % vm.name

        res = [machine['id'] if machine['name'] == clone_name for machine in response.json()]
        if res:
            # get id of cloned vm
            clone_id = res[0]
            api_url = url + '/restmachine/cloudapi/machines/get'
            api_body = {'machineId': clone_id}

            response = session.post(url=api_url, data=api_body)

            if response.status_code == 200:
                content = response.json()
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
                response_data = {'status_code': response.status_code,
                                 'content': response.content}
                service.model.data.result = RESULT_ERROR % str(response_data)+str(vm_id)
        else:
            failure = 'clone of %s is not created' % vm.name
            service.model.data.result = RESULT_FAILED % failure
    except Exception as e:
        service.model.data.result = RESULT_ERROR % (str(sys.exc_info()[:2]) + str(e))
    service.save()

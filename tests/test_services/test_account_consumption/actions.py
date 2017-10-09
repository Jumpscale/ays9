def init_actions_(service, args):
    """
    This needs to return an array of actions representing the depencies between actions.
    Looks at ACTION_DEPS in this module for an example of what is expected
    """

    # some default logic for simple actions

    return {
        'test': ['install']
    }


def authenticate(g8client):
    import requests
    url = 'https://' + g8client.model.data.url
    username = g8client.model.data.login
    password = g8client.model.data.password

    login_url = url + '/restmachine/system/usermanager/authenticate'
    credential = {'name': username,
                  'secret': password}

    session = requests.Session()
    session.post(url=login_url, data=credential)
    return session


def test(job):
    import sys, time
    service = job.service
    try:
        g8client = service.producers['g8client'][0]
        url = 'https://' + g8client.model.data.url
        session = authenticate(g8client)

        account = service.producers['account'][0]
        accountData = account.model.data
        cl = j.clients.openvcloud.getFromService(g8client)
        acc = cl.account_get(account.model.dbobj.name)
        space = acc.space_get('%sVdcConsumption' % account.model.dbobj.name, g8client.model.data.url.split('.')[0])
        while space.model['status'] != 'DEPLOYED':
            time.sleep(3)
            space = acc.space_get('%sVdcConsumption' % account.model.dbobj.name, g8client.model.data.url.split('.')[0])
        API_URL = url + '/restmachine/cloudapi/accounts/getConsumption?accountId={id}&start={start}&end={end}'.format(id=accountData.accountID,
                                                                                                                      start=accountData.consumptionFrom,
                                                                                                                      end=accountData.consumptionTo)

        response = session.get(url=API_URL)
        if account.model.data.consumptionData == response.content:
            service.model.data.result = 'OK : test_create_accounts_with_specs'
        else:
            service.model.data.result = 'FAILED : test_create_accounts_with_specs'
    except:
        service.model.data.result = 'ERROR :  %s %s' % ('test_create_accounts_with_specs', str(sys.exc_info()[:2]))
    finally:
        if 'g8client' in service.producers and 'account' in service.producers:
            session = authenticate(service.producers['g8client'][0])
            account = service.producers['account'][0]
            cl = j.clients.openvcloud.getFromService(g8client)
            acc = cl.account_get(account.model.dbobj.name)
            space = acc.space_get('%sVdcConsumption' % account.model.dbobj.name, g8client.model.data.url.split('.')[0])
            space.delete()
            API_URL = 'https://%s/restmachine/cloudapi/accounts/delete' % g8client.model.data.url
            API_BODY = {'accountId': account.model.data.accountID}
            session.post(url=API_URL, data=API_BODY)
    service.save()

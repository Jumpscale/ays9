def init_actions_(service, args):

    """

    this needs to returns an array of actions representing the depencies between actions.

    Looks at ACTION_DEPS in this module for an example of what is expected

    """
    # some default logic for simple actions
    return {

        'test': ['install']

    }


def test(job):
    import sys
    import time
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []
    retries = '5,10,15'
    try:
        ayscl = j.clients.atyourservice.get().api.ays
        repo = 'sample_repo_scheduler'
        ayscl.executeBlueprint(data=None, blueprint='with_retries.yaml', repository=repo)
        ayscl.createRun(data=None, repository=repo, query_params={'retries': retries}).json()
        retries = retries.split(',')
        service = ayscl.getServiceByName(name='scheduler1', role='actor', repository=repo).json()

        while len(service['data']['timeData']) < len(retries) + 1:
            time.sleep(5)
            service = ayscl.getServiceByName(name='scheduler1', role='actor', repository=repo).json()

        timeData = service['data']['timeData']
        if len(timeData) != len(retries) + 1:
            failures.append('Number of retries not the same as the number configured')

        for idx, item in enumerate(timeData):
            if idx == len(retries):
                break
            delay = timeData[idx + 1] - item
            if delay not in range(int(retries[idx]), int(retries[idx]) + 2):
                failures.append('Incorrect delay for retry number %s' % str(idx + 1))

        ayscl.executeBlueprint(data=None, blueprint='without_retries.yaml', repository=repo)
        retries = '0'
        ayscl.createRun(data=None, repository=repo, query_params={'retries': retries}).json()
        service = ayscl.getServiceByName(name='scheduler2', role='actor', repository=repo).json()

        while len(service['data']['timeData']) != len(retries):
            time.sleep(2)
            service = ayscl.getServiceByName(name='scheduler2', role='actor', repository=repo).json()

        timeData = service['data']['timeData']
        if len(timeData) != len(retries):
            failures.append("Run retried without retries configured")

        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)

    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        ayscl.destroyRepository(data={}, repository=repo)

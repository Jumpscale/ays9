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
    """
    Test timeouted actions
    """
    import sys
    import time
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []

    # HERE create run in sample_repo_timeout and wait for 10 seconds and check if the actions timedout.
    try:
        repo = 'sample_repo_timeout'
        cl = j.clients.atyourservice.get().api.ays
        cl.executeBlueprint(data=None, repository=repo, blueprint='test_timeout_actions.yaml')
        run = cl.createRun(data=None, repository=repo).json()
        runkey = run['key']
        # wait 10 seconds then checkout the run state and the jobs state.
        time.sleep(6)

        run = cl.getRun(runid=runkey, repository=repo).json()
        runstate = run['state']
        while runstate not in ['error', 'ok']:
            run = cl.getRun(runid=runkey, repository=repo).json()
            runstate = run['state']

        if runstate != 'error':
            failures.append("Wrong run state: Expected [{}] and Found [{}]".format("error", runstate))

        for step in run['steps']:
            for job_dict in step['jobs']:
                action_name = job_dict['action_name']
                if action_name in ['firstact', 'secondact']:
                    # the whole step should be in error state.
                    # job_dict state should be in error state.
                    if step['state'] != 'error':
                        failures.append("Wrong step [{}]state: Expected [{}] and Found [{}]".format(step['number'], "error", job_dict['state']))

                    if job_dict['state'] != 'error':
                        failures.append("Wrong job_dict [{}] state : Expected [{}] and Found [{}]".format(action_name, "error", job_dict['state']))

        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)
        else:
            model.data.result = RESULT_OK % 'ACTIONS TIMEDOUT CORRECTLY'

    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        cl.destroyRepository(data=None, repository=repo)

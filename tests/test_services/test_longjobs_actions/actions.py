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
    Test long actions
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
        repo = 'sample_repo_longjobs'
        cl = j.clients.atyourservice.get().api.ays
        # will try to execute a `longjob1` in main thread to make sure it doesn't block
        start = time.time()
        cl.executeBlueprint(data=None, repository=repo, blueprint='test_longjobsact.yaml')
        repos = cl.listRepositories().json()
        end = time.time()
        if end - start > 5:   # took more than 2 seconds? should never happen.
            failures.append("AYS server was blocked")

        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)
        else:
            model.data.result = RESULT_OK % 'AYS EXECUTED THE COROUTINE IN THE MAIN THREAD WITH NO PROBLEMS'
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        cl.destroyRepository(data=None, repository=repo)

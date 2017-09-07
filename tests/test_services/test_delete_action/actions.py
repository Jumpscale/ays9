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
    #try to remove service knotused which is not consumed by anyone.


    cl = j.clients.atyourservice.get().api.ays
    repo = "sample_repo_basicdelete"
    try:
        # prepare the repo.
        cl.executeBlueprint(data=None, repository=repo, blueprint="prepare.yaml")
        try:
            cl.deleteServiceByName(name='knotconsumed', role='dummy', repository=repo)
        except Exception as e:
            failures.append("Couldn't remove service knotconsumed even it's not consumed by anyone.")

        # now try to remove service kid which is consumed by cons1
        try:
            cl.deleteServiceByName(name='kid', role='chi', repository=repo)
        except Exception as e:
            if e.response.status_code == 403:
                pass 
        else:
            failures.append("Was able to remove service kid even it's consumed by service cons1")

        # now try to remove service kp which will remove kid which is consumed by cons1
        try:
            cl.deleteServiceByName(name='kp', role='dummy', repository=repo)
        except Exception as e:
            if e.response.status_code == 403:
                pass 
        else:
            failures.append("Was able to remove service kp even it's a parent of kid which is consumed by service cons1")

        try:
            cl.deleteServiceByName(name='k1', role='dummy', repository=repo)
        except Exception as e:
            failures.append("Wasn't able to remove service k1 even if won't break the minimum consumption required service cons1")

        try:
            cl.deleteServiceByName(name='k2', role='dummy', repository=repo)
        except Exception as e:
            if e.response.status_code == 403:
                pass 
        else:
            failures.append("Was able to remove service k2 even it will break the minimum consumption required service cons1")

        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)

    except Exception as e:
        raise e
    finally:
        cl.destroyRepository(data=None, repository=repo)
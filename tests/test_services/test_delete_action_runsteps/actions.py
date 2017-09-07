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

    cl = j.clients.atyourservice.get().api.ays
    repo = "sample_repo_basicdelete"

    def ensure_run():
        # execute run. (action install)
        run = cl.createRun(data=None, repository=repo).json()
        runid = run['key']

        run = cl.getRun(repository=repo, runid=runid).json()
        run = cl.executeRun(repository=repo, data=None, runid=runid).json()
        # run = cl.getRun(repository=repo, runid=runid).json()
        while run['state'] not in ['ok', 'error']:
            time.sleep(2)
            try:
                run = cl.getRun(repository=repo, runid=runid).json()
            except Exception as ex:
                print('Failed to retrieve run {} in repository {}'.format(runid, repo))
                break
        return run


    def validate_runsteps(expectedsteps, run):
        tobesteps = [[] for x in range(len(run['steps']))]
        if len(expectedsteps) != len(tobesteps):
            failures.append("Expected to have #{} steps but got #{} steps.".format(len(expectedsteps), len(tobesteps)))
        stepsinfo = []
        for s in run['steps']:
            stepsinfo.append([])
            for job in s['jobs']:
                stepsinfo[-1].append((job['service_name'], job['action_name']))

        print("Expected\n", expectedsteps)
        print("Got\n", stepsinfo)
        for stepidx, step in enumerate(run['steps']):
            jobset = set([(job['service_name'], job['action_name']) for job in step['jobs']])
            for expectedjob in expectedsteps[stepidx]:
                if expectedjob not in jobset:
                    failures.append("Expected to have {} - {} job. {}".format(*expectedjob, str(stepsinfo)))

    try:
        # prepare the repo.
        try:
            cl.executeBlueprint(data=None, repository=repo, blueprint="prepare.yaml")
        except Exception as ex:
            failures.append(str(ex))

        run = ensure_run()
        # delete knotconsumed
        try:
            cl.executeBlueprint(data=None, repository=repo, blueprint="delete_knotconsumed.yaml")
        except Exception as ex:
            failures.append(str(ex))

        run = ensure_run()
        expectedsteps = [[('knotconsumed', "stop")], [("knotconsumed", "uninstall")], [("knotconsumed", "delete")]]
        validate_runsteps(expectedsteps, run)

        # # delete cons1
        try:
            cl.executeBlueprint(data=None, repository=repo, blueprint="delete_cons1.yaml")
        except Exception as ex:
            failures.append(str(ex))

        run = ensure_run()
        expectedsteps = [[('cons1', "stop")], [("cons1", "uninstall")], [("cons1", "delete")]]
        validate_runsteps(expectedsteps, run)

        # delete kp
        try:
            cl.executeBlueprint(data=None, repository=repo, blueprint="delete_kp.yaml")
        except Exception as ex:
            failures.append(str(ex))

        run = ensure_run()

        expectedsteps = [[('kid', 'stop')], [('kid', 'uninstall'), ('kp', 'stop')], [('kid', 'delete'), ('kp', 'uninstall')], [('kp', 'delete')]]
        validate_runsteps(expectedsteps, run)

        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)
    except Exception as e:
        raise e
    finally:
        cl.destroyRepository(data=None, repository=repo)

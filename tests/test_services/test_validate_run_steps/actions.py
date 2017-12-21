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
    Tests parsing of a bp with/without default values
    """
    import sys
    import os
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []
    repos = []
    repo1 = 'sample_repo1'
    repo2 = 'sample_repo3'
    repos.extend([repo1, repo2])
    cwd = os.getcwd()
    try:
        ays_client = j.clients.atyourservice.get().api.ays
        bp_cmd = 'ays blueprint'
        run_cmd = 'ays run create -y --force -f'
        """
        Un-comment the following test when services dependencies across blueprints in the same repo are resolved.
        """
        # repo1_expected_steps = [
        #                         ('datacenter.ovh_germany1.install', 'datacenter.ovh_germany2.install',
        #                         'datacenter.ovh_germany3.install', 'sshkey.main.install'),
        #                         ('cockpit.cockpitv1.install', 'cockpit.cockpitv2.install')
        #                     ]
        #
        # repo1_info = ays_client.getRepository(repo1).json()
        # j.sal.fs.changeDir(repo1_info['path'])
        # j.tools.prefab.local.core.run(bp_cmd)
        #
        # j.tools.prefab.local.core.run(run_cmd)
        # runs = ays_client.listRuns(repository=repo1_info['name']).json()
        # run = runs[0]
        # run_info = ays_client.getRun(run['key'], repo1_info['name']).json()
        #
        # for index, step in enumerate(run_info['steps']):
        #     expected_step_jobs = repo1_expected_steps[index]
        #     for job_ in step['jobs']:
        #         job_name = '%s.%s.%s' % (job_['actor_name'], job_['service_name'], job_['action_name'])
        #         if job_name not in expected_step_jobs:
        #             failures.append('Job [%s] is added to step #%s unexpectedly' % (job_name, index + 1))


        expected_job_statuses = {
            'runtime_error_service.instance.install': 'ok',
            'runtime_error_service.instance.test': 'error',
            'runtime_error_service.instance.test2': 'ok',
            'runtime_error_service.instance.test3': 'new'
        }
        expected_step_statuses = ['ok', 'error', 'new']
        expected_run_status = 'error'

        repo2_info = ays_client.getRepository(repo2).json()
        j.sal.fs.changeDir(repo2_info['path'])
        j.tools.prefab.local.core.run(bp_cmd)
        j.tools.prefab.local.core.run(run_cmd)

        runs = ays_client.listRuns(repository=repo2_info['name']).json()
        run = runs[0]
        run_info = ays_client.getRun(run['key'], repo2_info['name']).json()


        for index, step in enumerate(run_info['steps']):
            for job_ in step['jobs']:
                job_name = '%s.%s.%s' % (job_['actor_name'], job_['service_name'], job_['action_name'])
                if job_name not in expected_job_statuses:
                    failures.append('Job [%s] is unexpected in step #%s' % (job_name, index + 1))
                elif expected_job_statuses[job_name] != job_['state']:
                    failures.append('Job [%s] has unexpected status [%s] expected [%s]' % (job_name, job_['state'], expected_job_statuses[job_name]))
            if step['state'] != expected_step_statuses[index]:
                failures.append('Step #%s has unexpected status [%s] expected [%s]' % (index + 1, step['state'], expected_step_statuses[index]))
        if run_info['state'] != expected_run_status:
            failures.append('Run has unexpected status [%s] expected [%s]' % (run_info['state'], expected_run_status))

        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        j.sal.fs.changeDir(cwd)
        for repo in repos:
            ays_client.destroyRepository(data={}, repository=repo)

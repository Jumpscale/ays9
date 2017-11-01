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
    Test recurring actions
    """
    import sys
    import os
    import time
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []
    repos = []
    try:
        expected_nr_of_jobs = 1
        curdir = os.getcwd()
        ays_client = j.clients.atyourservice.get()
        repo_name = 'sample_repo_recurring'
        bp_name = 'test_recurring_actions_1.yaml'
        repos.append(repo_name)
        path = ''
        for repo_info in ays_client.listRepositories().json():
            if repo_info['name'] == repo_name:
                path = repo_info['path']
                break
        execute_bp_res = ays_client.api.ays.executeBlueprint(data={}, blueprint=bp_name, repository=repo_name)
        if execute_bp_res.status_code == 200:
            start_time = time.time()
            time.sleep(60 * 2)
            nr_of_jobs = len(j.core.jobcontroller.db.jobs.find(actor='test_recurring_actions_1', service='instance',
                    action='execution_gt_period', fromEpoch=start_time))
            if nr_of_jobs > expected_nr_of_jobs:
                failures.append('Wrong number of jobs found. Expected [%s] found [%s]' % (expected_nr_of_jobs, nr_of_jobs))
        else:
            failures.append('Failed to execute blueprint [%s]' % bp_name)

        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)
        # remove recurring actions
        config_path = j.sal.fs.joinPaths(path, 'actorTemplates', 'test_recurring_actions_1')
        source_config = j.sal.fs.joinPaths(config_path, 'config.yaml')
        j.sal.fs.copyFile(source_config, "{}.bak".format(source_config))
        j.sal.fs.writeFile(source_config, "")
        ays_client.updateActor(data={}, actor='test_recurring_actions_1', repository=repo_name)
        nr_of_jobs = len(j.core.jobcontroller.db.jobs.find(actor='test_recurring_actions_1', service='instance',
        print("Number of jobs is %s" % nr_of_jobs)
        if nr_of_jobs != 0:
            failures.append("Failed to remove recurring actions")


    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        if repos:
            for repo in repos:
                try:
                    ays_client.api.ays.destroyRepository(data={}, repository=repo)
                except Exception as e:
                    j.logger.logging.error('Error while destroying repo %s. Error %s' % (repo, e) )

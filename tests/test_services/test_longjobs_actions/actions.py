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
        cl = j.clients.atyourservice.get().api.ays
        repo = 'sample_repo_longjobs'
        repos = cl.listRepositories().json()

        path = ''
        for repo_info in repos:
            if repo_info['name'] == repo:
                path = repo_info['path']
                break
        # start without any long jobs configured
        config_path = j.sal.fs.joinPaths(path, 'actorTemplates', 'longjobsact')
        source_config = j.sal.fs.joinPaths(config_path, 'config.yaml')
        modified_config = j.sal.fs.joinPaths(config_path, 'config.modified.yaml')
        j.sal.fs.copyFile(source_config, "{}.bak".format(source_config))
        j.sal.fs.writeFile(source_config, "")
        cl.executeBlueprint(data=None, repository=repo, blueprint='test_longjobsact.yaml')
        # update config to have a long running job
        j.sal.fs.copyFile("{}.bak".format(source_config), source_config)
        # call actor update
        original_nr_of_jobs = len(j.core.jobcontroller.db.jobs.list(actor='longjobsact', action='long1', state='running'))
        cl.updateActor(data={}, actor='longjobsact', repository=repo)cl = j.clients.atyourservice.get().api.ays
        repo = 'sample_repo_longjobs'
        repos = cl.listRepositories().json()

        path = ''
        for repo_info in repos:
            if repo_info['name'] == repo:
                path = repo_info['path']
                break
        # start without any long jobs configured
        config_path = j.sal.fs.joinPaths(path, 'actorTemplates', 'longjobsact')
        source_config = j.sal.fs.joinPaths(config_path, 'config.yaml')
        modified_config = j.sal.fs.joinPaths(config_path, 'config.modified.yaml')
        j.sal.fs.copyFile(source_config, "{}.bak".format(source_config))
        j.sal.fs.writeFile(source_config, "")
        cl.executeBlueprint(data=None, repository=repo, blueprint='test_longjobsact.yaml')
        # update config to have a long running job
        j.sal.fs.copyFile("{}.bak".format(source_config), source_config)
        # call actor update
        original_nr_of_jobs = len(j.core.jobcontroller.db.jobs.list(actor='longjobsact', action='long1', state='running'))
        cl.updateActor(data={}, actor='longjobsact', repository=repo)
        time.sleep(10)

        updated_nr_of_jobs = len(j.core.jobcontroller.db.jobs.list(actor='longjobsact', action='long1', state='running'))
        if updated_nr_of_jobs - original_nr_of_jobs != 1:
            failures.append("Updating actor did not add long jobs")

        # test update of the actor, after adding new long job to the config
        # update the actor's config
        config_path = j.sal.fs.joinPaths(path, 'actorTemplates', 'longjobsact')
        source_config = j.sal.fs.joinPaths(config_path, 'config.yaml')
        j.sal.fs.copyFile(source_config, '{}.bak'.format(source_config))
        j.sal.fs.copyFile(modified_config, source_config)

        # get the number of jobs for the new long job actor
        # this assumes that the test runs on the same machine where the ays is running
        original_nr_of_jobs = len(j.core.jobcontroller.db.jobs.list(actor='longjobsact', action='long2', state='running'))
        # call actor update
        cl.updateActor(data={}, actor='longjobsact', repository=repo)
        time.sleep(10)

        # check number of jobs
        updated_nr_of_jobs = len(j.core.jobcontroller.db.jobs.list(actor='longjobsact', action='long2', state='running'))
        if updated_nr_of_jobs - original_nr_of_jobs != 1:
            failures.append('Updating actor does not add long jobs')

        # now lets revert to the original config to remove the newly configured long running job
        job.service.executor.execute('cp {}.bak {}'.format(source_config, source_config))

        # call actor update
        cl.updateActor(data={}, actor='longjobsact', repository=repo)
        time.sleep(10)

        updated_nr_of_jobs = len(j.core.jobcontroller.db.jobs.list(actor='longjobsact', action='long2', state='running'))
        if updated_nr_of_jobs != original_nr_of_jobs:
            failures.append('Updating actor does not remove long jobs')

        updated_nr_of_jobs = len(j.core.jobcontroller.db.jobs.list(actor='longjobsact', action='long1', state='running'))
        if updated_nr_of_jobs - original_nr_of_jobs != 1:
            failures.append("Updating actor did not add long jobs")

        # test update of the actor, after adding new long job to the config
        # update the actor's config
        config_path = j.sal.fs.joinPaths(path, 'actorTemplates', 'longjobsact')
        source_config = j.sal.fs.joinPaths(config_path, 'config.yaml')
        j.sal.fs.copyFile(source_config, '{}.bak'.format(source_config))
        j.sal.fs.copyFile(modified_config, source_config)

        # get the number of jobs for the new long job actor
        # this assumes that the test runs on the same machine where the ays is running
        original_nr_of_jobs = len(j.core.jobcontroller.db.jobs.list(actor='longjobsact', action='long2', state='running'))
        # call actor update
        cl.updateActor(data={}, actor='longjobsact', repository=repo)
        time.sleep(10)

        # check number of jobs
        updated_nr_of_jobs = len(j.core.jobcontroller.db.jobs.list(actor='longjobsact', action='long2', state='running'))
        if updated_nr_of_jobs - original_nr_of_jobs != 1:
            failures.append('Updating actor does not add long jobs')

        # now lets revert to the original config to remove the newly configured long running job
        job.service.executor.execute('cp {}.bak {}'.format(source_config, source_config))

        # call actor update
        cl.updateActor(data={}, actor='longjobsact', repository=repo)
        time.sleep(10)
        
        updated_nr_of_jobs = len(j.core.jobcontroller.db.jobs.list(actor='longjobsact', action='long2', state='running'))
        if updated_nr_of_jobs != original_nr_of_jobs:
            failures.append('Updating actor does not remove long jobs')


        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)
        else:
            model.data.result = RESULT_OK % 'AYS EXECUTED THE COROUTINE IN THE MAIN THREAD WITH NO PROBLEMS'
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        cl.destroyRepository(data=None, repository=repo)

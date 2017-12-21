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
    Test recurring actions with hanging jobs
    """
    import sys
    import os
    import time
    import json
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []
    repos = []
    try:
        expected_nr_of_jobs = 0
        curdir = os.getcwd()
        ays_client = j.clients.atyourservice.get()
        repo_name = 'sample_repo_recurring'
        repos.append(repo_name)
        bp_name = 'test_recurring_actions_hanging_jobs.yaml'
        execute_bp_res = ays_client.api.ays.executeBlueprint(data={}, blueprint=bp_name, repository=repo_name)
        if execute_bp_res.status_code == 200:
            # create run
            data = json.loads(ays_client.api.ays.createRun(data={}, repository=repo_name).text)
            runid = data['key']
            # execute run
            start_time = time.time()
            data = json.loads(ays_client.api.ays.executeRun(data={}, runid=runid, repository=repo_name).text)
            time.sleep(35) # 30 seconds configured job timeout + 5 seconds
            end_time = time.time()
            nr_of_jobs = len(j.core.jobcontroller.db.jobs.find(actor='test_recurring_actions_1', service='hanging',
                    action='execute_hanging_job', fromEpoch=start_time,
                    toEpoch=end_time))
            if nr_of_jobs != expected_nr_of_jobs:
                failures.append('Wrong number of jobs found. Expected [%s] found [%s]' % (expected_nr_of_jobs, nr_of_jobs))
        else:
            failures.append('Failed to execute blueprint [%s]' % bp_name)

        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)

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

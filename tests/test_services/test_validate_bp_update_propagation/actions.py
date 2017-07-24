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
    Test bp update propagation
    """
    import sys
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []
    repos = []
    repo_path = j.sal.fs.joinPaths(j.dirs.codeDir, 'github/jumpscale/jumpscale_core8/tests/sample_repo2')
    bp_path = j.sal.fs.joinPaths(repo_path, 'blueprints', 'bp_validate_update_propagation.yaml')
    replacement_str = 'REPLACED'
    original_str = 'REPLACEME'
    replace_cmd = 'sed -i s/%s/%s/g %s' % (original_str, replacement_str, bp_path)
    expected_process_change_action_before_update = ['new']
    expected_process_change_action_after_update = ['ok', 'scheduled']
    service_name = 'instance'
    actors = ['repo2_template1', 'repo2_template2']
    try:
        j.atyourservice.server.reposDiscover()
        repo = j.atyourservice.server.repoGet(repo_path)
        repos.append(repo)
        repo.blueprintExecute(path=bp_path)
        for actor in actors:
        	srv = repo.servicesFind(name=service_name, actor=actor)
        	if not srv:
        		failures.append('Missing service [%s!%s] from repo [%s]' % (actor, service_name, repo))
        	else:
        		srv = srv[0]
        		action_state = str(srv.model.actions['processChange'].state)
        		if action_state not in expected_process_change_action_before_update:
        			failures.append("Unexpected state [%s] of action [processChange] for service[%s!%s]. Expected [%s]" % (action_state, 
        				actor, service_name, expected_process_change_action_before_update))

        job.service.executor.get_prefab().core.run(replace_cmd)

        repo.blueprintExecute(path=bp_path)
        for actor in actors:
        	srv = repo.servicesFind(name=service_name, actor=actor)
        	if not srv:
        		failures = 'Missing service [%s!%s] from repo [%s]' % (actor, service_name, repo)
        	else:
        		srv = srv[0]
        		action_state = str(srv.model.actions['processChange'].state)
        		if action_state not in expected_process_change_action_after_update:
        			failures.append("Unexpected state [%s] of action [processChange] for service[%s!%s]. Expected [%s]" % (action_state, 
        				actor, service_name, expected_process_change_action_after_update))
        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        replace_cmd = 'sed -i s/%s/%s/g %s' % (replacement_str, original_str, bp_path)
        job.service.executor.get_prefab().core.run(replace_cmd)
        for repo in repos:
            repo.destroy()
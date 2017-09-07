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
    Test ays update
    """
    import sys
    import os
    import json
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []
    repos = []
    cwd = os.getcwd()
    repo_name = 'sample_repo2'
    bp_name = 'bp_validate_update_propagation.yaml'
    repo_path = j.sal.fs.joinPaths(j.dirs.CODEDIR, 'github/jumpscale/ays9/tests/%s' % repo_name)
    bp_path = j.sal.fs.joinPaths(repo_path, 'blueprints', bp_name)
    replacement_str = 'REPLACED'
    original_str = 'REPLACEME'
    replace_cmd = 'sed -i s/%s/%s/g %s' % (original_str, replacement_str, bp_path)
    expected_process_change_action_before_update = ['new']
    expected_process_change_action_after_update = ['scheduled', 'ok']
    service_name = 'instance'
    actors = ['repo2_template1', 'repo2_template2']
    try:
        ays_client = j.clients.atyourservice.get()
        repos.append(repo_name)
        execute_bp_res = ays_client.api.ays.executeBlueprint(data={}, blueprint=bp_name, repository=repo_name)
        if execute_bp_res.status_code == 200:
            for actor in actors:
                find_service_res = ays_client.api.ays.getServiceByName(name=service_name, role=actor, repository=repo_name)
                if find_service_res.status_code == 200:
                    service = json.loads(find_service_res.text)
                    for action in service['actions']:
                        if action['name'] == 'processChange':
                            if action['state'] not in expected_process_change_action_before_update:
                                failures.append("Unexpected state [%s] of action [processChange] for service[%s!%s]. Expected [%s]" % (action['state'],
                    				actor, service_name, expected_process_change_action_before_update))
                            break
                else:
                    failures.append('Missing service [%s!%s] from repo [%s]' % (actor, service_name, repo_name))

            j.tools.prefab.local.core.run(replace_cmd)
            execute_bp_res = ays_client.api.ays.executeBlueprint(data={}, blueprint=bp_name, repository=repo_name)
            if execute_bp_res.status_code == 200:
                for actor in actors:
                    find_service_res = ays_client.api.ays.getServiceByName(name=service_name, role=actor, repository=repo_name)
                    if find_service_res.status_code == 200:
                        service = json.loads(find_service_res.text)
                        for action in service['actions']:
                            if action['name'] == 'processChange':
                                if action['state'] not in expected_process_change_action_after_update:
                                    failures.append("Unexpected state [%s] of action [processChange] for service[%s!%s]. Expected [%s]" % (action['state'],
                        				actor, service_name, expected_process_change_action_after_update))
                                break
                    else:
                        failures.append('Missing service [%s!%s] from repo [%s]' % (actor, service_name, repo_name))
            else:
                failures.append('Failed to execute blueprint [%s] after update' % bp_name)
        else:
            failures.append('Failed to execute blueprint [%s]' % bp_name)


        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])

    finally:
        job.service.save()
        j.sal.fs.changeDir(cwd)
        replace_cmd = 'sed -i s/%s/%s/g %s' % (replacement_str, original_str, bp_path)
        j.tools.prefab.local.core.run(replace_cmd)
        for repo in repos:
            ays_client.api.ays.destroyRepository(data={}, repository=repo)

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
    Test the created directory structure is corrected after ays blueprint on a test repo
    """
    import sys
    import os
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []
    expected_actors = ['cockpittesting', 'datacenter', 'sshkey']
    expected_files_per_actor = ['actions.py', 'actor.json', 'schema.capnp']
    actor_missing_msg = 'Actor folder [%s] does not exist'
    actor_file_missing_msg = 'File [%s] for actor [%s] is missing'
    service_file_missing_msg = 'Service file [%s] is missing'
    expected_services = {'datacenter!ovh_germany1':{
        # Un-comment the following when enabling the _bp_related1.yaml blueprint
        # 'cockpittesting!cockpitv1': {'files': ['data.json',
        # 'schema.capnp',
        # 'service.json']},
      'files': ['data.json', 'schema.capnp', 'service.json']},
      # Un-comment the following when enabling the _bp_related1.yaml blueprint
    #  'datacenter!ovh_germany2': {'files': ['data.json',
    #    'schema.capnp',
    #    'service.json']},
     'datacenter!ovh_germany3': {'cockpittesting!cockpitv2': {'files': ['data.json',
        'schema.capnp',
        'service.json']},
      'files': ['data.json', 'schema.capnp', 'service.json']},
     'sshkey!main': {'files': ['data.json', 'schema.capnp', 'service.json']}}
    cwd = os.getcwd()
    repos = []
    repo_name = 'sample_repo1'
    repo_path = j.sal.fs.joinPaths(j.dirs.CODEDIR, 'github/jumpscale/ays9/tests/%s' % repo_name)
    repos.append(repo_name)

    def check_service_dir(base_path, service):
            for service_name, service_info in service.items():
                if service_name != 'files':
                    path = j.sal.fs.joinPaths(base_path, service_name)
                    check_service_dir(path, service_info)
                else:
                    for service_file in service['files']:
                        if not j.sal.fs.exists(j.sal.fs.joinPaths(base_path, service_file)):
                            failures.append(service_file_missing_msg % j.sal.fs.joinPaths(base_path, service_file))
    try:
        ays_client = j.clients.atyourservice.get().api.ays
        blueprints = map(lambda item: item['name'], ays_client.listBlueprints(repo_name, query_params={'archived': False}).json())
        for blueprint in blueprints:
            ays_client.executeBlueprint(data={}, blueprint=blueprint, repository=repo_name)


        # validate directory structure
        for actor in expected_actors:
            if not j.sal.fs.exists(j.sal.fs.joinPaths(repo_path, 'actors', actor)):
                failures.append(actor_missing_msg % actor)
            else:
                for actor_file in expected_files_per_actor:
                    if not j.sal.fs.exists(j.sal.fs.joinPaths(repo_path, 'actors', actor, actor_file)):
                        failures.append(actor_file_missing_msg % (actor_file, actor))

        for service_name, service_info in expected_services.items():
            path = j.sal.fs.joinPaths(repo_path, 'services', service_name)
            check_service_dir(path, service_info)
        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)

    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        j.sal.fs.changeDir(cwd)
        for repo in repos:
            ays_client.destroyRepository(data={}, repository=repo)

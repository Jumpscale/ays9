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
    Tests auto bahavior
    """
    import sys
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    try:
        repo = j.atyourservice.repoGet('/opt/code/github/ays_automatic_cockpit_based_testing/sample_repo2')
        bp1_path = j.sal.fs.joinPaths(repo.path, 'blueprints', 'bp_nonexisting_services.yaml')
        try:
            repo.blueprintExecute(path=bp1_path)
        except Exception as ex:
            pass
        else:
            # the blueprint execute should fail since it tries to create a non-existing service
            model.data.result = RESULT_FAILED % ('Running blueprint with non-existing service does not fail')

        bp2_path = j.sal.fs.joinPaths(repo.path, 'blueprints', 'bp_conflicting_services_names.yaml')
        try:
            repo.blueprintExecute(path=bp2_path)
        except Exception as ex:
            pass
        else:
            # the blueprint execute should fail since it has conflieced services names
            model.data.result = RESULT_FAILED % ('Ruuning blueprint with conflict services names does not fail')
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
        
    job.service.save()

    

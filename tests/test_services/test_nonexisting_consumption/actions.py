def test(job):
    """
    Test ays will fail on wrong consumption
    """
    import sys
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []

    repo = None

    try:
        repo = 'sample_repo5'
        cl = j.clients.atyourservice.get().api.ays
        try:
            bp_resp = cl.executeBlueprint(data=None, repository=repo, blueprint='bp_non_exists_consume.yaml')
            if bp_resp.status_code == 200:
                failures.append("blueprint %s should have failed" % bp_name)
        except Exception:
            cl.deleteBlueprint('bp_non_exists_consume.yaml', job.service.aysrepo.name)
        if failures:
            model.data.result = RESULT_FAILED % '\n'.join(failures)

    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        if repo:
            cl.destroyRepository(data=None, repository=repo)

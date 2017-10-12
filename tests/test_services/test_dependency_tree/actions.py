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
    Tests dependency tree
    """
    import sys
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []
    try:
        # Tests parent relationship
        if job.service.name == 'parent':
            # make sure service has only one parent
            if job.service.parent.name != 'parent':
                failures.append(RESULT_FAILED % ("Service has the wrong parent"))
            elif model.dbobj.actorName not in job.service.parent.consumers:
                # validate that the current service is added as a consumers of the parent
                failures.append(RESULT_FAILED % ("Current service is not added in the consumers list of the parent"))

        if job.service.name == 'consumers':
            if 'test_dummy' not in job.service.producers:
                failures.append(RESULT_FAILED % ("test_dummy service is not added to producers"))
            elif len(job.service.producers['srv']) != 1:
                failures.append(RESULT_FAILED % ("Wrong number of producers of service srv"))
        if failures:
            model.data.result = '\n'.join(failures)
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])

    job.service.save()

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
        if job.service.name == "2min":
            if 'srv' not in job.service.producers:
                model.data.result = RESULT_FAILED % ("Producers not created while min value is 2")
            elif len(job.service.producers['srv']) != 2:
                model.data.result = RESULT_FAILED % ("Wrong number of producers is created")
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    job.service.save()

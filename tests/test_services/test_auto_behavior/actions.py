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
        if job.service.name == 'auto_parent':
            # make sure that the parent service is auto created
            if not job.service.parent.name.startswith('auto_'):
                model.data.result = RESULT_FAILED % ("Parent service did not automatically created")
        if job.service.name == "0min":
            if 'srv2' in job.service.producers:
                model.data.result = RESULT_FAILED % ("Producer created while min value is zero")
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    job.service.save()

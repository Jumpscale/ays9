def init_actions_(service, args):

    """

    this needs to returns an array of actions representing the depencies between actions.

    Looks at ACTION_DEPS in this module for an example of what is expected

    """
    # some default logic for simple actions
    return {

        'test': ['install'],
        'test2': ['install'],
        'test3': ['test2']

    }
    

def test(job):
    """
    Tests runtime error behavior
    """
    raise RuntimeError('Error from service %s!%s' % (job.service.model.dbobj.actorName, job.service.name))


def test2(job):
    """
    Fake action
    """
    pass

def test3(job):
    """
    Fake action
    """
    pass

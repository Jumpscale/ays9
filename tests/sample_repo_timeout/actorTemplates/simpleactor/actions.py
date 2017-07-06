def init_actions_(service, args):

    """

    this needs to returns an array of actions representing the depencies between actions.

    Looks at ACTION_DEPS in this module for an example of what is expected

    """
    # some default logic for simple actions
    return {

        'firstact': ['install'],
        'secondact': ['install'],

    }

def firstact(job):
    import time
    print("from firstact")
    time.sleep(50)



def secondact(job):
    import time
    print("from secondact")
    time.sleep(50)

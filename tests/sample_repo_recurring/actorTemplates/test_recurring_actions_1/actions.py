def init_actions_(service, args):

    """

    this needs to returns an array of actions representing the depencies between actions.

    Looks at ACTION_DEPS in this module for an example of what is expected

    """
    # some default logic for simple actions
    return {

        'execution_gt_period': ['install']

    }

def execution_gt_period(job):
    """
    Tests execution time of a service that takes more than the configured recurring period
    """
	# recurring period is 1m
    import time
    print('waiting...')
    time.sleep(5 * 60)


def execute_hanging_job(job):
    """
    Tests managing of hanging jobs
    """
    import time
    while True:
        time.sleep(5 * 60)

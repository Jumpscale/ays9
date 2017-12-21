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
    Tests that creating models of the service is correct with the correct attributes
    """
    failures = []
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    model_properties = ('role', 'parent', 'dictFiltered', 'name',
        'actionsSortedList', 'actionsCode', 'actionsSourceCode', 'actions', 'actionsRecurring', 'eventFilters',
        'actionsState')
    model_data_properties = ('testDummy', 'strAttr', 'listAttr')
    failed = False
    for prop in model_properties:
        if not hasattr(model, prop):
            failures.append("Model does not have property %s" % prop)
            # model.data.result = RESULT_FAILED % ("Model does not have property %s" % prop)
            # failed = True

    for prop in model_data_properties:
        if not hasattr(model.data, prop):
            failures.append('Model data does not have property %s' % prop)
    if failures:
        failures.append('%s' % (dir(model)))
        model.data.result = RESULT_FAILED % '\n'.join(failures)

    job.service.save()

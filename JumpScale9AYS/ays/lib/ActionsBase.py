"""
Default actions used when no specific actions are defined by actor templates
"""


def init_actions_(service, args):
    """
    this needs to returns an array of actions representing the depencies between actions.
    Looks at ACTION_DEPS in this module for an example of what is expected
    """

    # some default logic for simple actions

    action_required = args.get('action_required')

    if action_required in ['stop', 'uninstall']:
        for action_name, action_model in service.model.actions.items():
            if action_name in ['stop', 'uninstall']:
                continue
            if action_model.state == 'scheduled':
                action_model.state = 'new'

    if action_required in ['install']:
        for action_name, action_model in service.model.actions.items():
            if action_name in ['uninstall', 'stop'] and action_model.state == 'scheduled':
                action_model.state = 'new'


    if action_required == 'stop':
        if service.model.actionsState['start'] == 'sheduled':
            service.model.actionsState['start'] = 'new'

    if action_required == 'start':
        if service.model.actionsState['stop'] == 'sheduled':
            service.model.actionsState['stop'] = 'new'

    service.save()

    return {
        'init': [],
        'install': ['init'],
        'start': ['install'],
        'monitor': ['start'],
        'stop': [],
        'delete': ['uninstall'],
        'uninstall': ['stop'],
    }

def process_event_(service, args):
    """
    check the event, if match call relevant actions
    """

    event = args.get('event', None)
    if event is None:
        return

    channel = event.get('channel', '')
    command = event.get('command', '')
    action = event['action']
    secret = event.get('secret', '')

    for event_filter in service.model.eventfilters:
        if channel != '' and channel != event_filter.channel:
            continue

        if command != '' and command != event_filter.command:
            continue

        if secret != '' and secret != event_filter.secret:
            continue

    service._executeActionService(action)

# before each action this is called, this happens always in process
# if we return False then the action will not be executed
# if re return True, will be executed
# when method ends with _ it means will be executed in process & no job will be done
# def action_pre_(service, actionName):
#     pass
#     #
#     #
#     # if actionName in ["monitor", "halt", "check_up", "check_down",
#     #                          "check_requirements", "cleanup", "data_export", "data_import", "uninstall", "removedata",
#     #                          "consume", "actionstate_pre_check_","actionstate_post_"
#     #
#     # if actionName in ["monitor", "halt", "check_up", "check_down",
#     #                          "check_requirements", "cleanup", "data_export", "data_import", "uninstall", "removedata",
#     #                          "consume", "actionstate_pre_check_","actionstate_post_"
#     # from IPython import embed
#     # print ("DEBUG NOW precheck")
#     # embed()
#     # raise RuntimeError("stop debug here")
#     # return True
#
# # after each action this is called, this happens always in process
# # used to set the state of actions which can depend on this
# def action_post_(service, actionName):
#     from IPython import embed
#     print("DEBUG NOW statechange")
#     embed()
#     raise RuntimeError("stop debug here")
#
# def check_active(service):
#     """
#     check if service can be used in generic way, is it active
#     """
#     from IPython import embed
#     print("DEBUG NOW check_active")
#     embed()
#     raise RuntimeError("stop debug here")

# def change_hrd_template(self, service, originalhrd):
#     for methodname, obj in service.state.methods.items():
#         if methodname in ["install"]:
#             service.state.set(methodname, "CHANGEDHRD")
#             service.state.save()
#
# def change_hrd_instance(self, service, originalhrd):
#     for methodname, obj in service.state.methods.items():
#         if methodname in ["install"]:
#             service.state.set(methodname, "CHANGEDHRD")
#             service.state.save()
#
# def change_method(self, service, methodname):
#     service.state.set(methodname, "CHANGED")
#     service.state.save()
#
# def ask_telegram(self, username=None, message='', keyboard=[],
#                  expect_response=True, timeout=120, redis=None, channel=None):
#     """
#     username: str, telegram username of the person you want to send the message to
#     channel: str, telegram channel where the bot is an admin
#     message: str, message
#     keyboard: list of str: optionnal content for telegram keyboard.
#     expect_response: bool, if you want to wait for a response or not. if True, this method retuns the response
#         if not it return None
#     timeout: int, number of second we need to wait for a response
#     redis: redis client, optionnal if you want to use a specific reids client instead of j.core.db
#     """
#     redis = redis or j.core.db
#
#     key = "%s:%s" % (username, j.data.idgenerator.generateGUID())
#
#     out_evt = j.data.models.cockpit_event.Telegram()
#     out_evt.io = 'output'
#     out_evt.action = 'service.communication'
#     out_evt.args = {
#         'key': key,
#         'username': username,
#         'channel': channel,
#         'message': message,
#         'keyboard': keyboard,
#         'expect_response': expect_response
#     }
#     redis.publish('telegram', out_evt.to_json())
#     if expect_response:
#         data = redis.blpop(key, timeout=timeout)
#         if data is None:
#             raise j.exceptions.Timeout('timeout reached')
#
#         _, resp = data
#         resp = j.data.serializer.json.loads(resp)
#         if 'error' in resp:
#             raise j.exceptions.RuntimeError(
#                 'Unexpected error: %s' % resp['error'])
#
#         return resp['response']

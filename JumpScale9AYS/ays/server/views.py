from js9 import j
import os


def service_view(s):
    """
    generate a dict that represent a service from a service object
    """
    producers = []
    for prods in s.producers.values():
        for producer in prods:
            producers.append({'role': producer.model.role, 'name': producer.name})
    consumers = []
    for cons in s.consumers.values():
        for consumer in cons:
            consumers.append({'role': consumer.model.role, 'name': consumer.name})

    service = {
        'key': s.model.key,
        'name': s.name,
        'role': s.model.role,
        'repository': s.aysrepo.name,
        'data': j.data.serializer.json.loads(s.model.dataJSON),
        'state': s.model.dbobj.state.__str__(),
        'path': s.path,
        'actions': [],
        'parent': {'role': s.parent.model.role, 'name': s.parent.model.name} if s.parent else None,
        'producers': producers,
        'consumers': consumers,
        'children': [{'role': c.model.role, 'name': c.model.name} for c in s.children],
        'events': [],
    }

    for event_filter in s.model.eventFilters:
        service['events'].append({
            'actions': event_filter.actions,
            'command': event_filter.command,
            'channel': event_filter.channel,
            'tags': event_filter.tags.split(',')
        })

    actionsNames = sorted(s.model.actionsState.keys())
    for actionName in actionsNames:
        action = {
            'name': actionName,
            'code': s.model.actionsCode[actionName],
            'state': s.model.actionsState[actionName],
            'recurring': None,
        }
        if actionName in s.model.actionsRecurring:
            action['recurring'] = {
                'period': s.model.actionsRecurring[actionName].period,
                'last_run': s.model.actionsRecurring[actionName].lastRun,
            }
        service['actions'].append(action)

    return service


def run_view(run):
    """
    generate a dict that represent a run
    """
    obj = {
        'key': run.key,
        'state': str(run.state),
        'steps': [],
        'epoch': run.model.dbobj.lastModDate,
    }
    for step in run.steps:
        aystep = {
            'number': step.dbobj.number,
            'jobs': [],
            'state': step.state
        }
        for job in step.jobs:
            logs = []
            for log in job.model.dbobj.logs:
                log_dict = {}
                log_record = log.to_dict()
                log_dict['epoch'] = log_record['epoch'] if 'epoch' in log_record else None
                log_dict['log'] = log_record['log'] if 'log' in log_record else None
                log_dict['level'] = log_record['level'] if 'level' in log_record else None
                log_dict['category'] = log_record['category'] if 'category' in log_record else None
                log_dict['tags'] = log_record['tags'] if 'tags' in log_record else None
                logs.append(log_dict)

            aystep['jobs'].append({
                'key': job.model.key,
                'action_name': job.model.dbobj.actionName,
                'actor_name': job.model.dbobj.actorName,
                'service_key': job.model.dbobj.serviceKey,
                'service_name': job.model.dbobj.serviceName,
                'state': str(job.model.dbobj.state),
                'logs': logs,
                'result': job.model.dbobj.result
            })
        obj['steps'].append(aystep)
    obj['retries'] = run.get_retry_info()

    return obj


def job_view(job):
    view = {
        'key': job.key,
        'action_name': job.dbobj.actionName,
        'actor': job.dbobj.actorName,
        'service_key': job.dbobj.serviceKey,
        'service_name': job.dbobj.serviceName,
        'state': job.state,
        'logs': [],
        'result': job.dbobj.result
    }
    for log in job.dbobj.logs:
        view['logs'].append(log.to_dict())
    return view


def actor_view(a):
    """
    generate a dict that represent a service from a service object
    """
    actor = {
        'name': a.model.name,
        'schema': a.schemaCapnpText,
        'actions': []
    }

    actionsNames = sorted(a.model.actionsState.keys())
    for actionName in actionsNames:
        action = {
            'name': actionName,
            'code': a.model.actionsCode[actionName],
            'state': a.model.actionsState[actionName],
            'recurring': None,
        }
        if actionName in a.model.actionsRecurring:
            action['recurring'] = {
                'period': a.model.actionsRecurring[actionName].period,
            }
        actor['actions'].append(action)

    return actor


def blueprint_view(bp):
    return {
        'path': bp.path,
        'name': bp.name,
        'content':bp.content,
        'hash': bp.hash,
        'archived': not bp.active,
    }


def template_view(template):
    actions_path = j.sal.fs.joinPaths(template.path, 'actions.py')
    actions_file = None
    if j.sal.fs.exists(actions_path):
        actions_file = j.sal.fs.fileGetContents(actions_path)

    return {
        'name': template.name,
        'action': actions_file,
        'schema': template.schemaCapnpText,
        'config': template.configDict,
        'path': template.path,
        'role': template.role
    }


def repository_view(repo):
    try:
        git_url = repo.git.remoteUrl
    except:
        git_url = 'not defined'

    return {
        'name': repo.name,
        'path': repo.path,
        'git_url': git_url
    }

import json as JSON
from sanic.response import json, text
import jsonschema
from jsonschema import Draft4Validator
import capnp
from JumpScale9AYS.ays.lib.Blueprint import Blueprint
from JumpScale9AYS.ays.server.views import service_view
from JumpScale9AYS.ays.server.views import run_view
from JumpScale9AYS.ays.server.views import actor_view
from JumpScale9AYS.ays.server.views import blueprint_view
from JumpScale9AYS.ays.server.views import template_view
from JumpScale9AYS.ays.server.views import repository_view
from JumpScale9AYS.ays.server.views import job_view
from js9 import j

logger = j.logger.get('j.ays.sanic')

Blueprint_schema = JSON.load(open(j.sal.fs.joinPaths(j.sal.fs.getParent(__file__), 'schema/Blueprint_schema.json')))
Repository_schema = JSON.load(open(j.sal.fs.joinPaths(j.sal.fs.getParent(__file__), 'schema/Repository_schema.json')))
TemplateRepo_schema = JSON.load(open(j.sal.fs.joinPaths(j.sal.fs.getParent(__file__), 'schema/TemplateRepo_schema.json')))

AYS_REPO_DIR = j.dirs.VARDIR + '/ays_repos'


async def reload(request):
    try:
        j.atyourservice.server.reset()
        return json({})
    except Exception as e:
        return json({'error': e.message}, 500)


async def addTemplateRepo(request):
    '''
    add a new actor template repository
    It is handler for POST /ays/template_repo
    '''

    inputs = request.json
    try:
        Draft4Validator(TemplateRepo_schema).validate(inputs)
    except jsonschema.ValidationError as e:
        return text('Bad Request Body', 400)

    path = j.clients.git.pullGitRepo(url=inputs['url'], branch=inputs['branch'])

    # Register/update the cloned/pulled template repo
    template_repo_collection = j.atyourservice.server.templateRepos
    if path not in template_repo_collection._template_repos:
        template_repo_collection.create(path=path)
    else:
        template_repo_collection._template_repos[path]._load()

    return json({'message': 'repo added'}, 201)


async def listRepositories(request):
    '''
    list all repositorys
    It is handler for GET /ays/repository
    '''
    if j.atyourservice.server.aysRepos is None:
        j.atyourservice.server.start()
    if not j.atyourservice.server.aysRepos:
        return json([])
    repos = [repository_view(repo) for repo in j.atyourservice.server.aysRepos.list()]
    return json(repos)


async def createRepository(request):
    '''
    create a new repository
    It is handler for POST /ays/repository
    '''
    inputs = request.json
    try:
        Draft4Validator(Repository_schema).validate(inputs)
    except jsonschema.ValidationError as e:
        return text('Bad Request Body', 400)

    try:
        repo = get_repo(inputs['name'])
        return json({'error': 'AYS Repository "%s" already exsits' % inputs['name']}, 409)
    except j.exceptions.NotFound:
        pass

    try:
        path = j.sal.fs.joinPaths(AYS_REPO_DIR, inputs['name'])
        repo = j.atyourservice.server.aysRepos.create(path, git_url=inputs['git_url'])
        return json(repository_view(repo), 201)
    except Exception as err:
        # clean directory if something went wrong during creation
        if j.sal.fs.exists(path):
            j.sal.fs.removeDirTree(path)
        raise err


async def getRepository(request, repository):
    '''
    Get information of a repository
    It is handler for GET /ays/repository/<repository>
    '''

    try:
        repo = get_repo(repository)
        return json(repository_view(repo), 200)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)


async def deleteRepository(request, repository):
    '''
    Delete a repository
    It is handler for DELETE /ays/repository/<repository>
    '''

    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    await repo.delete()
    if j.sal.fs.exists(repo.path):
        j.sal.fs.removeDirTree(repo.path)

    return json({}, 204)


async def destroyRepository(request, repository):
    '''
    Delete a repository
    It is handler for POST /ays/repository/<repository>/destroy
    '''

    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    await repo.destroy()

    return json({}, 204)


async def getSchedulerStatus(request, repository):
    '''
    Return status of the scheduler
    It is handler for GET /ays/repository/<repository>/scheduler
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    return json({
        "status": repo.run_scheduler.status,
        "queueSize": repo.run_scheduler.queue.qsize()
    }, 200)


async def getCurrentRun(request, repository):
    '''
    Inspect if a run is currently beeing executed
    It is handler for GET /ays/repository/<repository>/scheduler/runs/running
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    if repo.run_scheduler.current_run:
        return json(run_view(repo.run_scheduler.current_run), 200)

    return json({}, 204)


async def updateTemplates(request, repository):
    '''
    update templates in a repo
    It is handler for GET /ays/repository/<repository>/template/update
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)
    repo_params = repository_view(repo)
    j.clients.git.pullGitRepo(url=repo_params['url'], dest=repo_params['path'])
    template_repo_collection = j.atyourservice.server.templateRepos
    template_repo_collection._template_repos[repo_params['path']]._load()
    return json({'message': 'Templates Updated'}, 200)

async def listTemplates(request, repository):
    '''
    list all templates
    It is handler for GET /ays/repository/<repository>/template
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)
    templates = [template_view(templ) for templ in repo.templates.values()]
    return json(templates, 200)


async def getTemplate(request, template, repository):
    '''
    Get a template
    It is handler for GET /ays/repository/<repository>/template/<template>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    template_names = list(repo.templates.keys())
    if template not in template_names:
        return json({'error': 'tempalte not found'}, 404)

    tmpl = repo.templates[template]
    template = template_view(tmpl)

    return json(template, 200)


async def listAYSTemplates(request):
    '''
    list all templates in ays_jumpscale
    It is hadnler for GET /ays/templates
    '''
    if j.atyourservice.server.aysRepos is None:
        j.atyourservice.server.start()
    try:
        templates = [template_view(templ) for templ in j.atyourservice.server.actorTemplates]
    except j.exceptions.NotFound as e:
        return json({'error': 'No templates found'}, 404)
    return json(templates, 200)


async def getAYSTemplate(request, template):
    '''
    list all templates in ays_jumpscale
    It is hadnler for GET /ays/templates
    '''
    if j.atyourservice.server.aysRepos is None:
        j.atyourservice.server.start()
    try:
        for tmpl in j.atyourservice.server.actorTemplates:
            if tmpl.name == template:
                template = template_view(tmpl)
                break
    except j.exceptions.NotFound as e:
        return json({'error': 'No templates found'}, 404)
    return json(template, 200)


async def listRuns(request, repository):
    '''
    list all runs of the repository
    It is handler for GET /ays/repository/<repository>/aysrun
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    runs = repo.runsList()
    runs = [{'key': run.model.key, 'epoch': run.model.dbobj.lastModDate, 'state': str(run.state)} for run in runs]

    return json(runs, 200)


async def createRun(request, repository):
    '''
    Create a run based on all the action scheduled. This call returns an AYSRun object describing what is going to hapen on the repository.
    This is an asyncronous call. To be notify of the status of the run when then execution is finised or when an error occurs, you need to specify a callback url.
    A post request will be send to this callback url with the status of the run and the key of the run. Using this key you can inspect in detail the result of the run
    using the 'GET /ays/repository/{repository}/aysrun/{aysrun_key}' endpoint.
    By specifying the retries as a string of comma seperated values it is possible to configure the retry delay of the run scheduler,
    with the number of retries being the number of specified values. For no retries send a string with only 0.
    It is handler for POST /ays/repository/<repository>/aysrun
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)
    simulate = j.data.types.bool.fromString(request.args.get('simulate', 'False'))
    callback_url = request.args.get('callback_url', None)
    retries = request.args.get('retries', None)
    try:
        to_execute = repo.findScheduledActions()
        run = repo.runCreate(to_execute, context={"token": extract_token(request)})
        run.save()
        if retries:
            retries = [int(x) for x in retries.split(',')]
            run.retries = retries
            run.save()
        if not simulate:
            await repo.run_scheduler.add(run)
        if callback_url:
            run.callbackUrl = callback_url
            run.save()
        return json(run_view(run), 200)

    except j.exceptions.Input as e:
        return json({'error': e.msgpub}, 500)
    except ValueError:
        return json({'error': 'Only numbers allowed for retry config'}, 400)


async def getRun(request, aysrun, repository):
    '''
    Get an aysrun
    It is handler for GET /ays/repository/<repository>/aysrun/<aysrun>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    try:
        aysrun_model = repo.runGet(aysrun)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    aysrun = aysrun_model.objectGet()
    return json(run_view(aysrun), 200)


async def getJob(request, jobid, repository):
    '''
    Get a job
    Handler for GET /ays/repository/<repository>/job<jobid>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)
    jobs = repo.jobsList()
    jobobj = None
    # Gets all jobs in repo and gets a job object from the specfied job id, if there is no match will return error message.
    for job in jobs:
        if job.key == jobid:
            jobobj = j.core.jobcontroller.db.jobs.get(jobid)
            break
    if not jobobj:
        return json({'error': 'no job with id %s found' % jobid}, 404)
    return json(job_view(jobobj), 200)


async def listJobs(request, repository):
    '''
    List all jobs that match the filters.
    filters are
    actor:str  Only list jobs of this actor
    service:str Only list jobs of this service
    action:str Only list jobs of this action
    type:str Only list jobs with this state
    serviceKey:str Only list jobs of this serviceKey
    fromEpoch:int Only list jobs from this epoch
    toEpoch:int Only list jobs till this epoch
    tags: comma-seperated list of tags to be included
    fields:str comma-seperated list of fields to be included in the response

    returns requested fields
    '''

    fields = request.args.get('fields', '')
    actor = request.args.get('actor', '')
    service = request.args.get('service', '')
    action = request.args.get('action', '')
    state = request.args.get('state', '')
    serviceKey = request.args.get('serviceKey', '')
    fromEpoch = request.args.get('fromEpoch', 0)
    toEpoch = request.args.get('toEpoch', 9999999999999)
    tags = request.args.get('tags', '')

    tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
    fields = [field.strip() for field in fields.split(',') if field.strip()]
    result = list()

    for job in j.core.jobcontroller.db.jobs.find(actor=actor, service=service, action=action, state=state, serviceKey=serviceKey, fromEpoch=fromEpoch, toEpoch=toEpoch, tags=tags):
        data = {'actor': job.dbobj.actorName, 'service': job.dbobj.serviceName, 'action': job.dbobj.actionName, 'state': str(job.dbobj.state), 'data': dict()}

        for field in fields:
            if not hasattr(job.dbobj, field):
                return json('No such field "{}" in job "{}" data'.format(field, job), 400)
            data['data'][field] = _sanitize(getattr(job.dbobj, field))
        result.append(data)
    result = sorted(result, key=lambda job: job['actor'])
    return json(result, 200)




async def deleteRun(request, aysrun, repository):
    '''
    Delete an aysrun
    It is handler for DELETE /ays/repository/<repository>/aysrun/<aysrun>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    try:
        repo.runDelete(aysrun)
        return json('run deleted succesfully', 200)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)


async def executeRun(request, aysrun, repository):
    """
    Execute a specific run
    """
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    try:
        aysrun_model = repo.runGet(aysrun)
        aysrun = aysrun_model.objectGet()
        await repo.run_scheduler.add(aysrun)

    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    except Exception as e:
        return json({'error': str(e)}, 500)

    return json(run_view(aysrun), 200)


async def listBlueprints(request, repository):
    '''
    List all blueprint
    It is handler for GET /ays/repository/<repository>/blueprint
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)
    include_archived = j.data.types.bool.fromString(request.args.get('archived', 'True'))
    blueprints = [{'name': blueprint.name} for blueprint in repo.blueprints]

    if include_archived:
        for blueprint in repo.blueprintsDisabled:
            blueprints.append({'name': blueprint.name})
    return json(blueprints, 200)


async def createBlueprint(request, repository):
    '''
    Create a new blueprint
    It is handler for POST /ays/repository/<repository>/blueprint
    '''

    inputs = request.json
    try:
        Draft4Validator(Blueprint_schema).validate(inputs)
    except jsonschema.ValidationError as e:
        return text('Bad Request Body :%s' % e, 400)

    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    new_name = inputs['name']
    content = inputs['content']
    names = [bp.name for bp in repo.blueprints]
    if new_name in names:
        return json({'error': "Blueprint with the name %s' already exists" % new_name}, 409)

    bp_path = j.sal.fs.joinPaths(repo.path, 'blueprints', new_name)
    try:
        j.sal.fs.writeFile(bp_path, content)
        blueprint = repo.blueprintGet(new_name)
    except Exception as e:
        print(str(e))
        if j.sal.fs.exists(bp_path):
            j.sal.fs.remove(bp_path)
        return json({'error': "Can't save new blueprint"}, 500)

    # check validity of input as blueprint syntax
    try:
        blueprint.validate()
    except:
        if j.sal.fs.exists(bp_path):
            j.sal.fs.remove(bp_path)
        return json({'error': "Invalid blueprint syntax"}, 500)

    return json(blueprint_view(blueprint), 201)


async def getBlueprint(request, blueprint, repository):
    '''
    Get a blueprint
    It is handler for GET /ays/repository/<repository>/blueprint/<blueprint>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    bp = None
    blueprints = repo.blueprints + repo.blueprintsDisabled
    for item in blueprints:
        if blueprint == item.name:
            bp = item
            break
    else:
        return json({'error': "No blueprint found with this name '%s'" % blueprint}, 404)

    return json(blueprint_view(bp), 200)


async def executeBlueprint(request, blueprint, repository):
    '''
    Execute the blueprint
    It is handler for POST /ays/repository/<repository>/blueprint/<blueprint>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    blueprints = repo.blueprints
    for item in blueprints:
        if item.name == blueprint:
            bp = item
            break
    else:
        return json({'error': "No blueprint found with this name '{}'".format(blueprint)}, 404)

    try:
        inputs = request.json
        message = inputs.get('message') if inputs else None
        jobkeys, msg = await repo.blueprintExecute(path=bp.path, context={'token': extract_token(request)},
                                                   message=message)

    except j.exceptions.Input as inputEx:
        error_msg = "Input Exception : \n %s" % str(inputEx)
        j.atyourservice.server.logger.exception(error_msg)
        return json({'error': str(inputEx)}, 400)

    except j.exceptions.NotFound as e:
        error_msg = "Input Exception : \n %s" % str(e)
        j.atyourservice.server.logger.exception(error_msg)
        return json({'error': str(e.message)}, 400)

    except Exception as e:
        error_msg = "Error during execution of the blueprint:\n %s" % str(e)
        j.atyourservice.server.logger.exception(error_msg)
        return json({'error': str(e)}, 500)
    # Returns json containing list of jobkeys in addition to the message. Will only return jobs with action process change.
    return json({'msg': msg, 'processChangeJobs': jobkeys})


async def updateBlueprint(request, blueprint, repository):
    '''
    Update existing blueprint
    It is handler for PUT /ays/repository/<repository>/blueprint/<blueprint>
    '''

    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    inputs = request.json
    try:
        Draft4Validator(Blueprint_schema).validate(inputs)
    except jsonschema.ValidationError as e:
        return text('Bad Request Body', 400)

    name = blueprint
    new_name = inputs['name']
    names = [bp.name for bp in repo.blueprints]
    names.extend([bp.name for bp in repo.blueprintsDisabled])
    if name not in names:
        return json({'error': "blueprint with the name %s not found" % name}, 404)
    # write content to the old file, then rename to the new name
    blueprint_path = j.sal.fs.joinPaths(repo.path, 'blueprints', name)
    blueprint = repo.blueprintGet(blueprint_path)
    content = inputs['content']

    newpb = Blueprint(aysrepo=repo, content=content, path="")
    if not newpb.is_valid:
        j.atyourservice.server.logger.exception("Invalid blueprint syntax.")
        return json({'error': str("Invalid blueprint syntax.")}, 400)
    else:
        blueprint.content = j.data.serializer.yaml.dumps(inputs['content'])
        blueprint.name = new_name
        j.sal.fs.writeFile(blueprint_path, content)
        # Rename the file
        new_path = j.sal.fs.joinPaths(repo.path, 'blueprints', new_name)
        j.sal.fs.renameFile(blueprint_path, new_path)
        blueprint = repo.blueprintGet(new_path)
        return json(blueprint_view(blueprint), 200)


async def deleteBlueprint(request, blueprint, repository):
    '''
    delete blueprint
    It is handler for DELETE /ays/repository/<repository>/blueprint/<blueprint>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    by_names = {bp.name: bp for bp in repo.blueprints}
    for bp in repo.blueprintsDisabled:
        by_names[bp.name] = bp

    if blueprint not in by_names:
        return json({'error': "blueprint with the name %s not found" % blueprint}, 404)

    bp = by_names[blueprint]

    if j.sal.fs.exists(bp.path):
        j.sal.fs.remove(bp.path)

    return json({}, 204)


async def archiveBlueprint(request, blueprint, repository):
    '''
    archive the blueprint
    It is handler for PUT /ays/repository/<repository>/blueprint/<blueprint>/archive
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    by_names = {bp.name: bp for bp in repo.blueprints}
    if blueprint not in by_names:
        return json({'error': "blueprint with the name %s not found" % blueprint}, 404)

    by_names[blueprint].disable()

    return json({'msg': 'Blueprint %s archived' % blueprint}, 200)


async def restoreBlueprint(request, blueprint, repository):
    '''
    restore the blueprint
    It is handler for PUT /ays/repository/<repository>/blueprint/<blueprint>/restore
    '''

    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    by_names = {bp.name: bp for bp in repo.blueprintsDisabled}
    if blueprint not in by_names:
        return json({'error': "blueprint with the name %s not found" % blueprint}, 404)

    by_names[blueprint].enable()

    return json({'msg': 'Blueprint %s restored' % blueprint}, 200)


async def listServices(request, repository):
    '''
    List all services in the repository
    It is handler for GET /ays/repository/<repository>/service
    '''
    actor = request.args.get('actor', '')
    role = request.args.get('role', '')
    service = request.args.get('service', '')
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    services = list()
    for s in repo.servicesFind(actor=actor, role=role, name=service):
        services.append({'actor': s.model.dbobj.actorName, 'name': s.name, 'role': s.model.role})
    services = sorted(services, key=lambda service: service['role'])

    return json(services, 200)


def _sanitize(value):
    if isinstance(value, (list, capnp.lib.capnp._DynamicListBuilder)):
        result = list()
        for item in value:
            result.append(_sanitize(item))
        return result
    elif isinstance(value, capnp.lib.capnp._DynamicStructBuilder):
        result = dict()
        for key, val in value.to_dict().items():
            result[key] = _sanitize(val)
        return result
    elif isinstance(value, dict):
        result = dict()
        for key, val in value.items():
            result[key] = _sanitize(val)
        return result
    elif isinstance(value, capnp.lib.capnp._DynamicEnum):
        return str(value)
    else:
        return value


async def listServicesByRole(request, role, repository):
    '''
    List all services of role 'role' in the repository
    It is handler for GET /ays/repository/<repository>/service/<role>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    parent = request.args.get('parent', '')
    fields = request.args.get('fields', '')

    consumed_service = request.args.get('consume', '')

    def flatten(l): return [item for sublist in l for item in sublist]

    fields = [field.strip() for field in fields.split(',') if field.strip()]
    result = list()
    if consumed_service:
        consumed_service = "service:{}".format(consumed_service)
    for s in repo.servicesFind(role=role, parent=parent):
        data = {'role': s.model.role, 'name': s.model.name, 'data': dict()}
        if consumed_service:
            allproducer_services_lists = s.producers.values()
            all_svs = list(map(str, flatten(allproducer_services_lists)))
            if consumed_service not in all_svs:
                continue

        for field in fields:
            if not hasattr(s.model.data, field):
                return json('No such field "{}" in service "{}" data'.format(field, s), 400)
            data['data'][field] = _sanitize(getattr(s.model.data, field))
        result.append(data)
    result = sorted(result, key=lambda service: service['role'])
    return json(result, 200)


async def getServiceByName(request, name, role, repository):
    '''
    Get a service name
    It is handler for GET /ays/repository/<repository>/service/<role>/<name>
    '''

    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    s = repo.serviceGet(role=role, instance=name, die=False)
    if s is None:
        return json({'error': 'Service not found'}, 404)

    return json(service_view(s), 200)


async def deleteServiceByName(request, name, role, repository):
    '''
    delete a service and all its children
    It is handler for DELETE /ays/repository/<repository>/service/<role>/<name>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    service = repo.serviceGet(role=role, instance=name, die=False)
    if service is None:
        return json({'error': 'Service role:%s name:%s not found in the repo %s' % (role, name, repository)}, 404)

    await service.asyncDelete()

    return json({}, 204)


async def listActors(request, repository):
    '''
    list all actors in the repository
    It is handler for GET /ays/repository/<repository>/actor
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    actors = [{'name': actor.model.name} for actor in repo.actors.values()]

    return json(actors, 200)


async def getActorByName(request, name, repository):
    '''
    Get an actor by name
    It is handler for GET /ays/repository/<repository>/actor/<name>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    try:
        actor = repo.actorGet(name=name)
    except j.exceptions.NotFound as e:
        json({'error': 'actor {} not found'.format(name)}, 404)

    return json(actor_view(actor), 200)


async def updateActor(request, name, repository):
    '''
    update an actor from a template to the last version
    It is handler for PUT /ays/repository/<repository>/actor/<name>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)

    try:
        actor = repo.actorGet(name=name)
    except j.exceptions.NotFound:
        return json({'error': 'actor {} not found'.format(name)}, 404)
    except Exception as err:
        return json({'error': 'unexpected error: {}'.format(err)}, 500)

    reschedule = j.data.types.bool.fromString(request.args.get('reschedule', False))
    try:
        actor.update(reschedule=reschedule, context={'token': extract_token(request)})
    except Exception as err:
        logger.error("error during actor update of {}: {}".format(name, err))
        return json({'error': 'unexpected error: {}'.format(err)}, 500)

    return json(actor_view(actor), 200)


def get_repo(name):
    """
    try to get a repo by his name.
    name is prepend with AYS_REPO_DIR to create the full path to the repo
    raise j.exceptions.NotFound if repo doesn't exists
    """
    if j.atyourservice.server.aysRepos is None:
        j.atyourservice.server.start()
    for repo in j.atyourservice.server.aysRepos.list():
        if name == repo.name:
            return repo

    raise j.exceptions.NotFound("Repository {} doesn't exists".format(name))


def extract_token(request):
    auth_header = request.headers.get('Authorization', None)
    if auth_header:
        ss = auth_header.split(' ', 1)
        if len(ss) == 2:
            return ss[1]
    return ""


async def configure_jslocation(request, repository):
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return json({'error': e.message}, 404)
    inputs = request.json

    instance = "{repo_name}_{instance_name}".format(repo_name=repo.name, instance_name=inputs["instance"])
    location = inputs["jslocation"]
    if not location.startswith("j."):
        return json({'error': "Invalid location"}, 400)
    try:
        j.tools.configmanager.path_configrepo
    except RuntimeError as e:
        if "Cannot find path" in str(e):
            print("Creating Js9config repo...")
            js9config_dir = "{}/github/jumpscale/js9config".format(j.dirs.CODEDIR)
            j.sal.fs.createDir(js9config_dir)
            j.sal.fs.createEmptyFile("{}/.jsconfig".format(js9config_dir))
    finally:
        js9_obj = j.tools.configmanager.js9_obj_get(location=location, instance=instance, data=inputs["data"])
        js9_obj.config.save()
        return json({'message': 'Instance configured'}, 201)

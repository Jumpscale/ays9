from sanic import Blueprint
from sanic.views import HTTPMethodView
from sanic.response import text
from JumpScale9AYS.ays.server import ays_api
from JumpScale9AYS.ays.server.oauth2_itsyouonline import oauth2_itsyouonline

ays_if = Blueprint('ays_if')


async def auth(request, funcname, **kwargs):
    code, msg = await oauth2_itsyouonline(["user:memberof:organization"]).check_token(request)
    if code != 200:
        return text(msg, code)
    func = getattr(ays_api, funcname)
    kwargs['request'] = request
    return await func(**kwargs)

class ays_reloadView(HTTPMethodView):

    async def post(self, request):
        return await auth(request=request, funcname='reload')

ays_if.add_route(ays_reloadView.as_view(), '/ays/reload')

class ays_repositoryView(HTTPMethodView):

    async def get(self, request):
        return await auth(request=request, funcname='listRepositories')

    async def post(self, request):
        return await auth(request=request, funcname='createRepository')

ays_if.add_route(ays_repositoryView.as_view(), '/ays/repository')

class ays_repository_byrepositoryView(HTTPMethodView):

    async def get(self, request, repository):
        return await auth(request=request, funcname='getRepository', repository=repository)

    async def delete(self, request, repository):
        return await auth(request=request, funcname='deleteRepository', repository=repository)

ays_if.add_route(ays_repository_byrepositoryView.as_view(), '/ays/repository/<repository>')

class ays_repository_byrepository_actorView(HTTPMethodView):

    async def get(self, request, repository):
        return await auth(request=request, funcname='listActors', repository=repository)

ays_if.add_route(ays_repository_byrepository_actorView.as_view(), '/ays/repository/<repository>/actor')

class ays_repository_byrepository_actor_byactorView(HTTPMethodView):

    async def get(self, request, actor, repository):
        return await auth(request=request, funcname='getActorByName', name=actor, repository=repository)

    async def put(self, request, actor, repository):
        return await auth(request=request, funcname='updateActor', name=actor, repository=repository)

ays_if.add_route(ays_repository_byrepository_actor_byactorView.as_view(), '/ays/repository/<repository>/actor/<actor>')

class ays_repository_byrepository_aysrunView(HTTPMethodView):

    async def get(self, request, repository):
        return await auth(request=request, funcname='listRuns', repository=repository)

    async def post(self, request, repository):
        return await auth(request=request, funcname='createRun', repository=repository)

ays_if.add_route(ays_repository_byrepository_aysrunView.as_view(), '/ays/repository/<repository>/aysrun')

class ays_repository_byrepository_aysrun_byrunidView(HTTPMethodView):

    async def get(self, request, runid, repository):
        return await auth(request=request, funcname='getRun', aysrun=runid, repository=repository)

    async def post(self, request, runid, repository):
        return await auth(request=request, funcname='executeRun', aysrun=runid, repository=repository)

    async def delete(self, request, runid, repository):
       return await auth(request=request, funcname='deleteRun', aysrun=runid, repository=repository)

ays_if.add_route(ays_repository_byrepository_aysrun_byrunidView.as_view(), '/ays/repository/<repository>/aysrun/<runid>')

class ays_repository_byrepository_blueprintView(HTTPMethodView):

    async def get(self, request, repository):
        return await auth(request=request, funcname='listBlueprints', repository=repository)

    async def post(self, request, repository):
        return await auth(request=request, funcname='createBlueprint', repository=repository)

ays_if.add_route(ays_repository_byrepository_blueprintView.as_view(), '/ays/repository/<repository>/blueprint')

class ays_repository_byrepository_blueprint_byblueprintView(HTTPMethodView):

    async def get(self, request, blueprint, repository):
        return await auth(request=request, funcname='getBlueprint', blueprint=blueprint, repository=repository)

    async def post(self, request, blueprint, repository):
        return await auth(request=request, funcname='executeBlueprint', blueprint=blueprint, repository=repository)

    async def put(self, request, blueprint, repository):
        return await auth(request=request, funcname='updateBlueprint', blueprint=blueprint, repository=repository)

    async def delete(self, request, blueprint, repository):
        return await auth(request=request, funcname='deleteBlueprint', blueprint=blueprint, repository=repository)

ays_if.add_route(ays_repository_byrepository_blueprint_byblueprintView.as_view(), '/ays/repository/<repository>/blueprint/<blueprint>')

class ays_repository_byrepository_blueprint_byblueprint_archiveView(HTTPMethodView):

    async def put(self, request, blueprint, repository):
        return await auth(request=request, funcname='archiveBlueprint', blueprint=blueprint, repository=repository)

ays_if.add_route(ays_repository_byrepository_blueprint_byblueprint_archiveView.as_view(), '/ays/repository/<repository>/blueprint/<blueprint>/archive')

class ays_repository_byrepository_blueprint_byblueprint_restoreView(HTTPMethodView):

    async def put(self, request, blueprint, repository):
        return await auth(request=request, funcname='restoreBlueprint', blueprint=blueprint, repository=repository)

ays_if.add_route(ays_repository_byrepository_blueprint_byblueprint_restoreView.as_view(), '/ays/repository/<repository>/blueprint/<blueprint>/restore')

class ays_repository_byrepository_destroyView(HTTPMethodView):

    async def post(self, request, repository):
        return await auth(request=request, funcname='destroyRepository', repository=repository)

ays_if.add_route(ays_repository_byrepository_destroyView.as_view(), '/ays/repository/<repository>/destroy')

class ays_repository_byrepository_job_byjobidView(HTTPMethodView):

    async def get(self, request, jobid, repository):
        return await auth(request=request, funcname='getJob', jobid=jobid, repository=repository)

ays_if.add_route(ays_repository_byrepository_job_byjobidView.as_view(), '/ays/repository/<repository>/job/<jobid>')

class ays_repository_byrepository_jobView(HTTPMethodView):

    async def get(self, request, repository):
        return await auth(request=request, funcname='listJobs', repository=repository)

ays_if.add_route(ays_repository_byrepository_jobView.as_view(), '/ays/repository/<repository>/job')

class ays_repository_byrepository_serviceView(HTTPMethodView):

    async def get(self, request, repository):
        return await auth(request=request, funcname='listServices', repository=repository)

ays_if.add_route(ays_repository_byrepository_serviceView.as_view(), '/ays/repository/<repository>/service')

class ays_repository_byrepository_service_byroleView(HTTPMethodView):

    async def get(self, request, role, repository):
        return await auth(request=request, funcname='listServicesByRole', role=role, repository=repository)

ays_if.add_route(ays_repository_byrepository_service_byroleView.as_view(), '/ays/repository/<repository>/service/<role>')

class ays_repository_byrepository_service_byrole_bynameView(HTTPMethodView):

    async def get(self, request, name, role, repository):
        return await auth(request=request, funcname='getServiceByName', name=name, role=role, repository=repository)

    async def delete(self, request, name, role, repository):
        return await auth(request=request, funcname='deleteServiceByName', name=name, role=role, repository=repository)

ays_if.add_route(ays_repository_byrepository_service_byrole_bynameView.as_view(), '/ays/repository/<repository>/service/<role>/<name>')

class ays_repository_byrepository_templateView(HTTPMethodView):

    async def get(self, request, repository):
        return await auth(request=request, funcname='listTemplates', repository=repository)

ays_if.add_route(ays_repository_byrepository_templateView.as_view(), '/ays/repository/<repository>/template')


class ays_repository_byrepository_templateUpdate(HTTPMethodView):

    async def get(self, request, repository):
        return await auth(request=request, funcname='updateTemplates', repository=repository)


ays_if.add_route(ays_repository_byrepository_templateUpdate.as_view(), '/ays/repository/<repository>/template/update')


class ays_repository_byrepository_template_bynameView(HTTPMethodView):

    async def get(self, request, name, repository):
        return await auth(request=request, funcname='getTemplate', template=name, repository=repository)

ays_if.add_route(ays_repository_byrepository_template_bynameView.as_view(), '/ays/repository/<repository>/template/<name>')

class ays_template_repoView(HTTPMethodView):

    async def post(self, request):
        return await auth(request=request, funcname='addTemplateRepo')

ays_if.add_route(ays_template_repoView.as_view(), '/ays/template_repo')

class ays_templatesView(HTTPMethodView):

    async def get(self, request):
        return await auth(request=request, funcname='listAYSTemplates')

ays_if.add_route(ays_templatesView.as_view(), '/ays/templates')

class ays_templates_bynameView(HTTPMethodView):

    async def get(self, request, name):
        return await auth(request=request, funcname='getAYSTemplate', template=name)

ays_if.add_route(ays_templates_bynameView.as_view(), '/ays/templates/<name>')

class ays_repository_byrepository_schedulerView(HTTPMethodView):

    async def get(self, request, repository):
        return await auth(request=request, funcname='getSchedulerStatus', repository=repository)

ays_if.add_route(ays_repository_byrepository_schedulerView.as_view(), '/ays/repository/<repository>/scheduler')


class ays_repository_byrepository_scheduler_runs_runningView(HTTPMethodView):

    async def get(self, request, repository):
        return await auth(request=request, funcname='getCurrentRun', repository=repository)

ays_if.add_route(ays_repository_byrepository_scheduler_runs_runningView.as_view(), '/ays/repository/<repository>/scheduler/running')


class ays_configure_jslocation(HTTPMethodView):
    async def post(self, request, repository):
        return await auth(request=request, funcname='configure_jslocation', repository=repository)


ays_if.add_route(ays_configure_jslocation.as_view(), '/ays/repository/<repository>/configure-jslocation')

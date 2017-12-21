class AysService:
    def __init__(self, client):
        self.client = client



    def reload(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        reload AYS
        It is method for POST /ays/reload
        """
        uri = self.client.base_url + "/ays/reload"
        return self.client.post(uri, data, headers, query_params, content_type)


    def getActorByName(self, actor, repository, headers=None, query_params=None, content_type="application/json"):
        """
        Get an actor by name
        It is method for GET /ays/repository/{repository}/actor/{actor}
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/actor/"+actor
        return self.client.get(uri, headers, query_params, content_type)


    def updateActor(self, data, actor, repository, headers=None, query_params=None, content_type="application/json"):
        """
        update an actor from a template to the last version
        It is method for PUT /ays/repository/{repository}/actor/{actor}
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/actor/"+actor
        return self.client.put(uri, data, headers, query_params, content_type)


    def listActors(self, repository, headers=None, query_params=None, content_type="application/json"):
        """
        list all actors in the repository
        It is method for GET /ays/repository/{repository}/actor
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/actor"
        return self.client.get(uri, headers, query_params, content_type)


    def deleteRun(self, runid, repository, headers=None, query_params=None, content_type="application/json"):
        """
        delete a run
        It is method for DELETE /ays/repository/{repository}/aysrun/{runid}
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/aysrun/"+runid
        return self.client.delete(uri, headers, query_params, content_type)


    def getRun(self, runid, repository, headers=None, query_params=None, content_type="application/json"):
        """
        Get an aysrun
        It is method for GET /ays/repository/{repository}/aysrun/{runid}
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/aysrun/"+runid
        return self.client.get(uri, headers, query_params, content_type)

    def getJob(self, jobid, repository, headers=None, query_params=None, content_type="application/json"):
        """
        Get a jobid
        It is method for GET /ays/repository/{repository}/job{jobid}
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/job/"+jobid
        return self.client.get(uri, headers, query_params, content_type)

    def listJobs(self, repository, headers=None, query_params=None, content_type="application/json"):
        """
        List all jobs in a repo
        It is method for GET /ays/repository/{repository}/job
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
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/job"
        return self.client.get(uri, headers, query_params, content_type)

    def executeRun(self, data, runid, repository, headers=None, query_params=None, content_type="application/json"):
        """
        execute an aysrun
        It is method for POST /ays/repository/{repository}/aysrun/{runid}
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/aysrun/"+runid
        return self.client.post(uri, data, headers, query_params, content_type)


    def listRuns(self, repository, headers=None, query_params=None, content_type="application/json"):
        """
        list all runs of the repository
        It is method for GET /ays/repository/{repository}/aysrun
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/aysrun"
        return self.client.get(uri, headers, query_params, content_type)


    def createRun(self, data, repository, headers=None, query_params=None, content_type="application/json"):
        """
        Create a run based on all the action scheduled. This call returns an AYSRun object describing what is going to hapen on the repository.
        This is an asyncronous call. To be notify of the status of the run when then execution is finised or when an error occurs, you need to specify a callback url.
        A post request will be send to this callback url with the status of the run and the key of the run. Using this key you can inspect in detail the result of the run
        using the 'GET /ays/repository/{repository}/aysrun/{aysrun_key}' endpoint
        It is method for POST /ays/repository/{repository}/aysrun
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/aysrun"
        return self.client.post(uri, data, headers, query_params, content_type)


    def archiveBlueprint(self, data, blueprint, repository, headers=None, query_params=None, content_type="application/json"):
        """
        archive the blueprint
        It is method for PUT /ays/repository/{repository}/blueprint/{blueprint}/archive
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/blueprint/"+blueprint+"/archive"
        return self.client.put(uri, data, headers, query_params, content_type)


    def restoreBlueprint(self, data, blueprint, repository, headers=None, query_params=None, content_type="application/json"):
        """
        restore the blueprint
        It is method for PUT /ays/repository/{repository}/blueprint/{blueprint}/restore
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/blueprint/"+blueprint+"/restore"
        return self.client.put(uri, data, headers, query_params, content_type)


    def deleteBlueprint(self, blueprint, repository, headers=None, query_params=None, content_type="application/json"):
        """
        delete blueprint
        It is method for DELETE /ays/repository/{repository}/blueprint/{blueprint}
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/blueprint/"+blueprint
        return self.client.delete(uri, headers, query_params, content_type)


    def getBlueprint(self, blueprint, repository, headers=None, query_params=None, content_type="application/json"):
        """
        Get a blueprint
        It is method for GET /ays/repository/{repository}/blueprint/{blueprint}
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/blueprint/"+blueprint
        return self.client.get(uri, headers, query_params, content_type)


    def executeBlueprint(self, data, blueprint, repository, headers=None, query_params=None, content_type="application/json"):
        """
        Execute the blueprint
        It is method for POST /ays/repository/{repository}/blueprint/{blueprint}
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/blueprint/"+blueprint
        return self.client.post(uri, data, headers, query_params, content_type)


    def updateBlueprint(self, data, blueprint, repository, headers=None, query_params=None, content_type="application/json"):
        """
        Update existing blueprint
        It is method for PUT /ays/repository/{repository}/blueprint/{blueprint}
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/blueprint/"+blueprint
        return self.client.put(uri, data, headers, query_params, content_type)


    def listBlueprints(self, repository, headers=None, query_params=None, content_type="application/json"):
        """
        List all blueprint
        It is method for GET /ays/repository/{repository}/blueprint
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/blueprint"
        return self.client.get(uri, headers, query_params, content_type)


    def createBlueprint(self, data, repository, headers=None, query_params=None, content_type="application/json"):
        """
        Create a new blueprint
        It is method for POST /ays/repository/{repository}/blueprint
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/blueprint"
        return self.client.post(uri, data, headers, query_params, content_type)


    def destroyRepository(self, data, repository, headers=None, query_params=None, content_type="application/json"):
        """
        destroy repo without deleting it from FS
        It is method for POST /ays/repository/{repository}/destroy
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/destroy"
        return self.client.post(uri, data, headers, query_params, content_type)


    def getCurrentRun(self, repository, headers=None, query_params=None, content_type="application/json"):
        """
        Inspect if a run is currently beeing executed
        It is method for GET /ays/repository/{repository}/scheduler/running
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/scheduler/running"
        return self.client.get(uri, headers, query_params, content_type)


    def getSchedulerStatus(self, repository, headers=None, query_params=None, content_type="application/json"):
        """
        Return status of the scheduler
        It is method for GET /ays/repository/{repository}/scheduler
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/scheduler"
        return self.client.get(uri, headers, query_params, content_type)


    def deleteServiceByName(self, name, role, repository, headers=None, query_params=None, content_type="application/json"):
        """
        delete a service and all its children
        It is method for DELETE /ays/repository/{repository}/service/{role}/{name}
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/service/"+role+"/"+name
        return self.client.delete(uri, headers, query_params, content_type)


    def getServiceByName(self, name, role, repository, headers=None, query_params=None, content_type="application/json"):
        """
        Get a service by its name
        It is method for GET /ays/repository/{repository}/service/{role}/{name}
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/service/"+role+"/"+name
        return self.client.get(uri, headers, query_params, content_type)


    def listServicesByRole(self, role, repository, headers=None, query_params=None, content_type="application/json"):
        """
        List all services of role 'role' in the repository
        It is method for GET /ays/repository/{repository}/service/{role}
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/service/"+role
        return self.client.get(uri, headers, query_params, content_type)


    def listServices(self, repository, headers=None, query_params=None, content_type="application/json"):
        """
        List all services in the repository
        It is method for GET /ays/repository/{repository}/service
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/service"
        return self.client.get(uri, headers, query_params, content_type)


    def getTemplate(self, name, repository, headers=None, query_params=None, content_type="application/json"):
        """
        Get a template
        It is method for GET /ays/repository/{repository}/template/{name}
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/template/"+name
        return self.client.get(uri, headers, query_params, content_type)


    def listTemplates(self, repository, headers=None, query_params=None, content_type="application/json"):
        """
        list all templates
        It is method for GET /ays/repository/{repository}/template
        """
        uri = self.client.base_url + "/ays/repository/"+repository+"/template"
        return self.client.get(uri, headers, query_params, content_type)


    def deleteRepository(self, repository, headers=None, query_params=None, content_type="application/json"):
        """
        Delete a repository
        It is method for DELETE /ays/repository/{repository}
        """
        uri = self.client.base_url + "/ays/repository/"+repository
        return self.client.delete(uri, headers, query_params, content_type)


    def getRepository(self, repository, headers=None, query_params=None, content_type="application/json"):
        """
        Get information of a repository
        It is method for GET /ays/repository/{repository}
        """
        uri = self.client.base_url + "/ays/repository/"+repository
        return self.client.get(uri, headers, query_params, content_type)


    def listRepositories(self, headers=None, query_params=None, content_type="application/json"):
        """
        list all repositorys
        It is method for GET /ays/repository
        """
        uri = self.client.base_url + "/ays/repository"
        return self.client.get(uri, headers, query_params, content_type)


    def createRepository(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        create a new repository
        It is method for POST /ays/repository
        """
        uri = self.client.base_url + "/ays/repository"
        return self.client.post(uri, data, headers, query_params, content_type)


    def addTemplateRepo(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        add a new actor template repository
        It is method for POST /ays/template_repo
        """
        uri = self.client.base_url + "/ays/template_repo"
        return self.client.post(uri, data, headers, query_params, content_type)


    def getAYSTemplate(self, name, headers=None, query_params=None, content_type="application/json"):
        """
        get an AYS template
        It is method for GET /ays/templates/{name}
        """
        uri = self.client.base_url + "/ays/templates/"+name
        return self.client.get(uri, headers, query_params, content_type)


    def listAYSTemplates(self, headers=None, query_params=None, content_type="application/json"):
        """
        list all AYS templates
        It is method for GET /ays/templates
        """
        uri = self.client.base_url + "/ays/templates"
        return self.client.get(uri, headers, query_params, content_type)

    def updateTemplates(self, repository, headers=None, query_params=None, content_type="application/json"):
        """
        update all actors in template repo
        """
        uri = self.client.base_url + "/ays/repository/" + repository + "/template/" + "update"
        return self.client.get(uri, headers, query_params, content_type)

[actor] @dbtype:mem,fs
    """
    gateway to atyourservice
    """
    method:templatesUpdate
        """
        update templates repo
        """
        result:json

    method:addTemplateRepo
        """
        Add a new service template repository.
        """
        var:url str,, Service template repository URL
        var:branch str,, Branch of the repo to use default:master
        result:str

    method:listTemplates
        """
        list ays templates
        """
        var:repository str,,services in that base path will only be returned otherwise all paths @tags: optional
        result:json

    method:getTemplate
        """
        list ays templates
        """
        var:repository str,,repository in which look for template
        var:template str,,template name
        result:json

    method:createBlueprint
        """
        create a blueprint
        """
        var:repository str,,blueprints in that base path will only be returned otherwise all paths
        var:blueprint str,,blueprint name @tags: optional
        var:role str,,role @tags: optional
        result:json

    method:executeBlueprint
        """
        execute all blueprints
        """
        var:repository str,,blueprints in that base path will only be returned otherwise all paths
        var:blueprint str,,blueprint name @tags: optional
        result:json

    method:executeBlueprints
        """
        execute all blueprints
        """
        var:repository str,,repo name
        result:json
        
    method:quickBlueprint
        """
        execute all blueprints
        """
        var:repository str,,blueprints in that base path will only be returned otherwise all paths
        var:name str,,name of blueprint. if empty will archive with name being time @tags: optional
        var:contents str,,content of blueprint
        result:json


    method:updateBlueprint
        """
        update blueprint
        """
        var:repository str,,blueprints in that base path will only be returned otherwise all paths
        var:blueprint str,,name of blueprint. if empty will archive with name being time @tags: optional
        var:contents str,,content of blueprint
        result:json

    method:listBlueprints
        """
        list all blueprints
        """
        var:repository str,,blueprints in that base path will only be returned otherwise all paths @tags: optional
        var:archived bool,,include archived blueprints or not @tags: optional default:True
        result:json

    method:archiveBlueprint
        """
        archive a blueprint
        """
        var:repository str,,repository name
        var:blueprint str,,blueprint name
        result:json

    method:restoreBlueprint
        """
        restore a blueprint
        """
        var:repository str,,repository name
        var:blueprint str,, blueprint name
        result:json

    method:createRepo
        """
        Create AYS repository
        """
        var:name str,, repository name
        result:json

    method:deleteRepo
        """
        Destroy AYS repository
        """
        var:repository str,, repository name
        result:json

    method:deleteRuns
        """
        Destroy all runs in DB.
        """
        result:json

    method:simulate
        """
        Run simulate on AYS repository
        """
        var:repository str,, repository name
        result:json

    method:deleteService
        """
        Uninstall a service
        """
        var:repository str,, repository name
        var:role str,, role of the services to delete @tag optional
        var:instance str,, instance name of the service to delete @tag optional
        result:json


    method:commit
        """
        Commit change in the cockpit repo.
        """
        var:branch str,, branch to commit on
        var:push bool,, push after commit
        var:message str,, name of the repository @tag optional
        result:json

    method:createRun
        """
        """
        var:repository str,, repository name


    method:getRun
        """
        """
        var:repository str,, repository name
        var:runid str,, run id
        result:json

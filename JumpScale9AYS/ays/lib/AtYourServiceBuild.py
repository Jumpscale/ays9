from js9 import j

"""
This module holds common logic for the execution of the builds using AYS

Code that needs to be executed by the build services is repetitive so we bundle the logic here
and just pass the build service as argument to our methods
"""


def ensure_container(service, root):
    """
    @param service: service object
    @service type: JumpScale9AYS.ays.lib.Service.Service
    @param root: specify if this container need to be created from a previous build image or if it's a root docker build
    @root type: boolean

    ensure_container makes sure that a docker container where the build will happens is created

    This methods needs to be called during the init action of the build service.
    It will create a node.docker service named with the actor name of the service so we know what we are going to
    build inside.

    Some consuption is also done between the build service and the node.docker created so the order of execution is
    correct
    """
    repo = service.aysrepo

    # look for build host os service
    builder_host = None
    for parent in service.parents:
        if parent.model.role == 'os':
            builder_host = parent
            break
    else:
        raise j.exceptions.AYSNotFound("Can't find builder host os service")

    # check if we have a parent. parent creates a docker image wihch we need to use as our base
    parent_actor_name = None
    if service.parent:
        parent_actor_name = service.parent.model.dbobj.actorName

    base_image = ("aysbuilding_%s" % parent_actor_name) if (not root and parent_actor_name) else 'jumpscale/ubuntu1604'

    # create the node.docker service we are going to do the build
    result = repo.servicesFind(actor='node.docker', name=service.model.dbobj.actorName)
    if len(result) > 0:
        builder_docker = result[0]
    else:
        actor = repo.actorGet('node.docker')
        args = {
            'os': builder_host.model.name,
            'image': base_image,
            'ports': ['22'],
            'ssh.login': 'root',
            'ssh.password': 'gig1234',
            'volumes': [
                '/mnt/building/opt:/opt',
                '/mnt/building/optvar:/optvar'
            ],
            'sshkey': builder_host.model.data.sshkey
        }
        builder_docker = actor.serviceCreate(instance=service.model.dbobj.actorName, args=args)
        # all the producer need to consume this docker so we are sure the depencencies are done before
        for producers in service.producers.values():
            for prod in producers:
                builder_docker.consume(prod)

    # consume the os layer of the docker where we are going to built.
    # to make sure it's installed before this service
    builder_os = repo.serviceGet('os', service.model.dbobj.actorName)
    service.consume(builder_os)

    service.saveAll()


def build(service, build_func, build_destination='/mnt/building'):
    # look for os of the node.docker that will be use to build
    os = None
    for prod in service.producers['os']:
        if prod.model.name == service.model.dbobj.actorName:
            os = prod
            break
    else:
        raise j.exceptions.AYSNotFound("can't find os layer of builder docker for %s" % service.model.dbobj.actorName)

    # make sure the container use the last version of the image available
    # service.logger.info("recreate docker container for the build")
    # for action in ['uninstall', 'install']:
    #     job = os.parent.getJob(action)
    #     job.method(job)

    # make sure the building destinatin exists
    prefab = os.executor.get_prefab()
    executordict = '$VARDIR/jsexecutor.json'
    if prefab.core.file_exists(executordict):
        prefab.core.run('rm %s' % executordict)
    prefab.core.configReset()
    prefab.core.dir_ensure(build_destination)

    # do the actual building
    build_func(prefab)

    cfg_path = prefab.core.replace("$BASEDIR/build.yaml")
    branch = service.model.data.branch if hasattr(service.model.data, 'branch') else 'master'
    versions = {service.model.role: branch}
    if prefab.core.file_exists(cfg_path):
        config = j.data.serializer.yaml.loads(prefab.core.file_read(cfg_path))
        config.update(versions)
    else:
        config = versions
    prefab.core.file_write(cfg_path, j.data.serializer.yaml.dumps(config))


    # find the os layer of the build host
    os_hostbuidler = None
    to_check = [service]
    to_check.extend(service.parents)
    for item in to_check:
        if hasattr(item.model.data, 'builderHost'):
            os_hostbuidler = service.aysrepo.servicesFind(item.model.data.builderHost, actor='os(\..*)?')[0]
            break
    else:
        raise j.exceptions.AYSNotFound("can't find os layer of builder host")

    prefab_host = os_hostbuidler.executor.get_prefab()
    # create a new image from the result of the build
    docker_id = os.parent.model.data.id
    cmd = 'docker commit {id} aysbuilding_{name}'.format(id=docker_id, name=service.model.dbobj.actorName)
    prefab_host.core.run(cmd)

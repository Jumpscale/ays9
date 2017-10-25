from js9 import j

def input(job):
    #can also use node as argument, looks more logical than os
    if "node" in job.model.args:
        res = job.model.args
        res["os"] = res["node"]
        res.pop("node")
        job.model.args = res

    return job.model.args

def install(job):
    '''
    make sure docker is properly installed (use prefab functionality)
    '''
    service = job.service
    prefab = service.executor.prefab
    if not prefab.virtualization.docker.isInstalled():
        prefab.virtualization.docker.install()

    if not prefab.virtualization.dockercompose.isInstalled():
        prefab.virtualization.dockercompose.install()


def start(job):
    pass


def stop(job):
    '''
    @todo stop all docker instances
    '''
    pass


def monitor(job):
    '''
    @todo monitor that docker is properly working
    '''
    pass

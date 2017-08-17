from js9 import j


def install(job):
    job.model().create()


def model(job):
    service = job.service
    c = service.executor.get_prefab()
    controller = c.systemservices.kvm._controller
    vmpool = service.producers['vmpool'][0]
    name = service.model.dbobj.name
    size = service.model.data.size
    backingStore = service.producers.get('backingStore', [None])[0]

    pool = j.sal.kvm.Pool(controller, vmpool.model.data.name)
    return j.sal.kvm.Disk(controller, pool, name, size, backingStore.path() if backingStore else None)

def install(job):
    prefab = job.service.executor.get_prefab()
    data = job.service.model.data

    # create a pool for the images and virtual disks
    pool = prefab.systemservices.kvm.storage_pools.create(name=data.name)
    data.path = pool.poolpath

    job.service.model.actions['uninstall'].state = 'new'
    job.service.saveAll()

def uninstall(job):
    prefab = job.service.executor.get_prefab()
    data = job.service.model.data

    # delete a pool
    # destroy all volume in the pool before deleting the pool
    pool = prefab.systemservices.kvm.storage_pools.get_by_name(name=data.name)
    pool.delete()

    data.path = ''

    job.service.model.actions['install'].state = 'new'
    job.service.saveAll()

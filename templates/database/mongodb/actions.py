def install(job):
    prefab = job.service.executor.get_prefab()
    name = 'mongod_%s' % job.service.name
    prefab.apps.mongodb.install(start=True, name=name)


def start(job):
    prefab = job.service.executor.get_prefab()
    name = 'mongod_%s' % job.service.name
    prefab.apps.mongodb.start(name)


def stop(job):
    prefab = job.service.executor.get_prefab()
    name = 'mongod_%s' % job.service.name
    prefab.apps.mongodb.stop(name)

def install(job):
    prefab = job.service.executor.prefab
    name = 'mongod_%s' % job.service.name
    prefab.db.mongodb.install(start=True, name=name)


def start(job):
    prefab = job.service.executor.prefab
    name = 'mongod_%s' % job.service.name
    prefab.db.mongodb.start(name)


def stop(job):
    prefab = job.service.executor.prefab
    name = 'mongod_%s' % job.service.name
    prefab.db.mongodb.stop(name)

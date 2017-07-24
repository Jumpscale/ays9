def install(job):
    service = job.service
    prefab = service.executor.get_prefab()

    prefab.apps.redis.install()
    prefab.apps.redis.start(
        name=service.name,
        ip=service.model.data.host if service.model.data.host != '' else None,
        port=service.model.data.port,
        unixsocket=service.model.data.unixsocket if service.model.data.unixsocket != '' else None,
        maxram=service.model.data.maxram,
        appendonly=service.model.data.appendonly)


def start(job):
    service = job.service
    prefab = service.executor.get_prefab()

    prefab.apps.redis.install()
    prefab.apps.redis.start(
        name=service.name,
        ip=service.model.data.host if service.model.data.host != '' else None,
        port=service.model.data.port,
        unixsocket=service.model.data.unixsocket if service.model.data.unixsocket != '' else None,
        maxram=service.model.data.maxram,
        appendonly=service.model.data.appendonly)


def stop(job):
    service = job.service
    prefab = service.executor.get_prefab()
    prefab.apps.redis.stop(job.service.name)

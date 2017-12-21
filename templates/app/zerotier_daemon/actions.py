def install(job):
    """
    Installing zerotier
    """
    service = job.service
    prefab = service.parent.executor.prefab

    # build and install zerotier
    prefab.system.package.update()
    zerotier_client = prefab.network.zerotier
    zerotier_client.build()
    zerotier_client.install()
    zerotier_client.start()
    for network in service.producers['network']:
        zerotier_client.join_network(network.model.data.id)

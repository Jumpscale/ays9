def install(job):
    """
    Installing owncloud
    """
    service = job.service
    prefab = service.executor.get_prefab()

    clusterId = service.model.data.clusterId
    # dbname = service.model.data.dbname
    # dbuser = service.model.data.dbuser
    # dbpassword = service.model.data.dbpass

    prefab.apps.tidb.start()
    prefab.package.mdupdate()
    prefab.package.install('mysql-client-core-5.7')

def install(job):
    """
    Installing owncloud
    """
    service = job.service
    prefab = service.executor.prefab

    clusterId = service.model.data.clusterId
    # dbname = service.model.data.dbname
    # dbuser = service.model.data.dbuser
    # dbpassword = service.model.data.dbpass

    prefab.apps.tidb.start()
    prefab.system.package.mdupdate()
    prefab.system.package.install('mysql-client-core-5.7')

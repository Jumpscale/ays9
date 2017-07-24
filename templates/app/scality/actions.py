def install(job):
    """
    Scality is already available in the sandbox, no need to install or copy files.
    Instead, we will reconfigure it to use the provided storage and meta paths.
    """
    service = job.service

    prefab = service.executor.get_prefab()
    prefab.core.dir_ensure(service.model.data.storageData)
    prefab.core.dir_ensure(service.model.data.storageMeta)

    env = {
        'S3DATAPATH': service.model.data.storageData,
        'S3METADATAPATH': service.model.data.storageMeta,
    }

    app_path = '/opt/jumpscale8/apps/S3'
    config_path = j.sal.fs.joinPaths(app_path, 'config.json')
    config_str = prefab.core.file_read(config_path)
    config = j.data.serializer.json.loads(config_str)
    config['regions'] = {
        'us-east-1': [service.model.data.domain]
    }

    prefab.core.file_write(
        config_path,
        j.data.serializer.json.dumps(config, indent=2)
    )

    accessKey = service.model.data.keyAccess
    secretKey = service.model.data.keySecret

    PASSWD = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if accessKey == "":
        #generate new access and secret
        accessKey =  j.data.idgenerator.generatePasswd(12, al=PASSWD)
        secretKey =  j.data.idgenerator.generatePasswd(12, al=PASSWD)

        service.model.data.keyAccess = accessKey
        service.model.data.keySecret = secretKey
        service.saveAll()

    #setup user auth
    config_path = j.sal.fs.joinPaths(app_path, 'conf', 'authdata.json')
    config_str = prefab.core.file_read(config_path)
    config = j.data.serializer.json.loads(config_str)
    default_account = config['accounts'][0]
    default_account['name'] = 'ays'
    default_account['keys'] = [
        {
            'access': accessKey,
            'secret': secretKey,
        }
    ]
    default_account.pop('users', None)

    config['accounts'] = [default_account]
    prefab.core.file_write(
        config_path,
        j.data.serializer.json.dumps(config, indent=2)
    )

    pm = prefab.processmanager.get('tmux')
    pm.ensure(
        name='scalityS3',
        cmd='npm start',
        env=env,
        path=app_path
    )

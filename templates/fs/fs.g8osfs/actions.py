def install(job):
    prefab = job.service.executor.prefab

    prefab.system.package.mdupdate()
    prefab.system.package.install('fuse')
    bin_location = '/usr/local/bin/fs'
    prefab.core.dir_ensure('/usr/local/bin')
    prefab.core.file_download('https://stor.jumpscale.org/public/fs', bin_location)
    prefab.core.file_attribs('/usr/local/bin/fs', '0550')

    service = job.service
    prefab = service.executor.prefab

    final_config = {
        'mount': [],
        'backend': {},
        'aydostor': {},
    }

    targets = []

    for config in service.producers['vfs_config']:
        # TODO download flist
        flist_path = prefab.core.replace('$TMPDIR/%s' % j.sal.fs.getBaseName(config.model.data.mountFlist))
        prefab.core.file_download(config.model.data.mountFlist, flist_path, overwrite=True)

        targets.append(config.model.data.mountMountpoint)

        mount = {
            'path': config.model.data.mountMountpoint,
            'flist': flist_path,
            'backend': config.name,
            'mode': config.model.data.mountMode,
            'trim_base': config.model.data.mountTrimbase,
            'trim': config.model.data.mountTrim,
        }

        prefab.core.dir_ensure(config.model.data.backendPath)
        backend = {
            'path': config.model.data.backendPath,
            'stor': config.name,
            'namespace': config.model.data.backendNamespace,
            'upload': config.model.data.backendUpload,
            'encrypted': config.model.data.backendEncrypted,
            'user_rsa': config.model.data.backendUserRsa,
            'store_rsa': config.model.data.backendStoreRsa,
            'aydostor_push_cron': config.model.data.backendPush,
            'cleanup_cron': config.model.data.backendCleanupCron,
            'cleanup_older_than': config.model.data.backendCleanupOld,
        }

        store = {
            'addr': config.model.data.storeUrl,
            'login': config.model.data.storeLogin,
            'passwd': config.model.data.storePassword,
        }

        final_config['mount'].append(mount)
        final_config['backend'][config.name] = backend
        final_config['aydostor'][config.name] = store

    # make sure nonthing is already mounted
    for mount in final_config['mount']:
        cmd = 'umount -fl %s' % mount['path']
        prefab.core.run(cmd, die=False)

    # create all mountpoints but make sure we don't create folder inside mountpoints in the cases
    # we would have a mountpoint inside another
    # e.g for two mountpoints:
    # /mnt/root
    # /mnt/root/opt
    # we only create /mnt/root
    tocreate = {m['path'] for m in final_config['mount']}
    todelete = set()
    for path in tocreate:
        if j.sal.fs.getParent(path) in tocreate:
            todelete.add(path)

    for path in tocreate.difference(todelete):
        prefab.core.dir_ensure(path)

    # write config
    config_path = prefab.core.replace('$JSCFGDIR/fs/%s.toml' % service.name)
    prefab.core.file_write(config_path, j.data.serializer.toml.dumps(final_config))

    # create service
    pm = prefab.processmanager.get('tmux')
    bin_location = prefab.core.command_location('fs')
    cmd = '%s -config %s' % (bin_location, config_path)
    pm.ensure("fs_%s" % service.name, cmd=cmd, env={}, path='$JSCFGDIR/fs', descr='G8OS FS', autostart=True, wait=180)

    # wait until all targets are actually mounted
    # We wait max 1 min per target
    # NOTE: in real life, once one target is ready all targets would be there
    import time
    for target in targets:
        trials = 12
        while trials > 0:
            code, _, _ = prefab.core.run('mount | grep -P "on {}\s"'.format(target), die=False)
            if code != 0:
                # not found yet. We sleep for 5 seconds
                time.sleep(5)
            else:
                break
            trials -= 1

def start(job):
    # the start needs all the steps from install so just re-call install
    service = job.service
    job = service.getJob('install')
    job.executeInProcess()

def stop(job):
    service = job.service
    prefab = service.executor.prefab

    pm = prefab.processmanager.get('tmux')
    pm.stop('fs_%s' % service.name)

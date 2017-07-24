def install(job):
    prefab = job.service.executor.get_prefab()

    # For now we download FS from there. when we have proper VM image it will be installed already
    if not prefab.core.command_check('fs'):
        prefab.core.dir_ensure('$BINDIR')
        prefab.core.file_download('https://stor.jumpscale.org/public/fs', '$BINDIR/fs')
        prefab.core.file_attribs('$BINDIR/fs', '0550')


def start(job):
    prefab = job.service.executor.get_prefab()
    service = job.service
    actor = service.aysrepo.actorGet(name=service.model.dbobj.actorName)

    prefab.core.dir_ensure('$JSCFGDIR/fs/flists')
    for flist in actor.model.dbobj.flists:
        args = {}
        args['flist_path'] = prefab.core.replace('$JSCFGDIR/fs/flists/%s' % flist.name)
        prefab.core.file_write(args['flist_path'], flist.content)
        args['mountpoint'] = flist.mountpoint
        args['mode'] = flist.mode.__str__().upper()
        args['namespace'] = flist.namespace
        args['store_url'] = flist.storeUrl

        prefab.core.dir_ensure(args['mountpoint'])

        config = """
        [[mount]]
            path="{mountpoint}"
            flist="{flist_path}"
            backend="main"
            mode = "{mode}"
            trim_base = true

        [backend.main]
            path="/storage/fs_backend"
            stor="stor1"
            namespace="{namespace}"

            upload=false
            encrypted=false
            # encrypted=true
            # user_rsa="user.rsa"
            # store_rsa="store.rsa"

            aydostor_push_cron="@every 1m"
            cleanup_cron="@every 1m"
            cleanup_older_than=1 #in hours

        [aydostor.stor1]
            addr="{store_url}"
        """.format(**args)
        config_path = prefab.core.replace('$JSCFGDIR/fs/%s.toml' % flist.name)
        prefab.core.file_write(config_path, config)

        pm = prefab.processmanager.get('tmux')
        cmd = '$BINDIR/fs -config %s' % config_path
        pm.ensure("fs_%s" % flist.name, cmd=cmd, env={}, path='$JSCFGDIR/fs', descr='G8OS FS')


def stop(job):
    prefab = job.service.executor.get_prefab()
    service = job.service
    actor = service.aysrepo.actorGet(name=service.model.dbobj.actorName)

    for flist in actor.model.dbobj.flists:
        config_path = prefab.core.replace('$JSCFGDIR/fs/%s.toml' % flist.name)
        flist_config = prefab.core.file_read(config_path)
        flist_config = j.data.serializer.toml.loads(flist_config)

        pm = prefab.processmanager.get('tmux')
        pm.stop('fs_%s' % flist.name)

        for mount in flist_config['mount']:
            cmd = 'umount -fl %s' % mount['path']
            prefab.core.run(cmd)


def processChange(job):
    service = job.service
    category = job.model.args.get('changeCategory', None)

    if category == 'config':
        service.runAction('stop')
        service.runAction('start')


def start_flist(job):
    args = job.model.args
    prefab = job.service.executor.get_prefab()

    prefab.core.dir_ensure('$JSCFGDIR/fs/flists')
    flist_content = j.sal.fs.fileGetContents(args['flist'])
    flist_name = j.sal.fs.getBaseName(args['flist'])
    args['flist_path'] = prefab.core.replace('$JSCFGDIR/fs/flists/%s' % flist_name)
    prefab.core.file_write(args['flist_path'], flist_content)

    prefab.core.dir_ensure(args['mount_path'])

    config = """
    [[mount]]
        path="{mount_path}"
        flist="{flist_path}"
        backend="main"
        mode = "{mode}"
        trim_base = true

    [backend.main]
        path="/storage/fs_backend"
        stor="stor1"
        namespace="{namespace}"

        upload=false
        encrypted=false
        # encrypted=true
        # user_rsa="user.rsa"
        # store_rsa="store.rsa"

        aydostor_push_cron="@every 1m"
        cleanup_cron="@every 1m"
        cleanup_older_than=1 #in hours

    [aydostor.stor1]
        addr="{store_addr}"
    """.format(**args)
    config_path = prefab.core.replace('$JSCFGDIR/fs/%s.toml' % flist_name)
    prefab.core.file_write(config_path, config)

    pm = prefab.processmanager.get('tmux')
    cmd = '$BINDIR/fs -config %s' % config_path
    pm.ensure("fs_%s" % flist_name, cmd=cmd, env={}, path='$JSCFGDIR/fs', descr='G8OS FS')


def stop_flist(job):
    prefab = job.service.executor.get_prefab()
    args = job.model.args

    flist_name = j.sal.fs.getBaseName(args['flist'])
    config_path = prefab.core.replace('$JSCFGDIR/fs/%s.toml' % flist_name)
    flist_config = prefab.core.file_read(config_path)
    flist_config = j.data.serializer.toml.loads(flist_config)

    pm = prefab.processmanager.get('tmux')
    pm.stop('fs_%s' % flist_name)

    for mount in flist_config['mount']:
        cmd = 'umount -fl %s' % mount['path']
        prefab.core.run(cmd)

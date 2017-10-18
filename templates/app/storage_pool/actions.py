def init_actions_(service, args):
    # some default logic for simple actions
    return {
        'snapshot': ['install'],
        'replicate': ['install']
    }

def install(job):
    return

def snapshot(job):
    service = job.service
    if not service.model.data.snapshot:
        return
    from datetime import date
    d = date.today()
    os = service.producers['os'][0]
    path = service.model.data.path
    root_path = service.producers['fs'][0].model.data.mount
    snapshots_path = j.sal.fs.joinPaths(root_path, 'snapshots')
    prefab = os.executor.prefab
    prefab.core.dir_ensure(snapshots_path)
    prefab.core.sudomode = True
    prefab.btrfs.snapshotReadOnlyCreate(path, j.sal.fs.joinPaths(snapshots_path, '%s_%d_%d_%d' % (service.name,
                                                                                                   d.year,
                                                                                                   d.month,
                                                                                                   d.day)))

def replicate(job):
    service = job.service
    if not service.model.data.replicate or not service.model.data.pools:
        return
    os_base = service.producers['os'][0]
    prefab_base = os_base.executor.prefab
    prefab_base.system.rsync.build()

    for pool in service.producers['storage_pool']:
        os_remote = pool.producers['os'][0]
        node_remote = os_remote.producers['node'][0]
        address = node_remote.model.data.ipPrivate
        prefab_remote = os_remote.executor.prefab
        content = ''
        if node_remote.producers['sshkey']:
            key = node_remote.producers['sshkey'][0].model.data.keyPub
            content = node_remote.producers['sshkey'][0].model.data.keyPriv
            prefab_base.core.dir_ensure('$HOMEDIR/.ssh')
            prefab_base.core.file_write('$HOMEDIR/.ssh/default.rsa', content, mode=700)
        else:
            keypath = prefab_base.ssh.keygen()
            key = prefab_base.file_read()
        prefab_remote.ssh.authorize('root', key)
        path = j.sal.fs.joinPaths(service.producers['fs'][0].model.data.mount, service.model.data.path)
        tmp = '/'.split('/')
        tmp.pop()
        path_remote = "/".join(tmp)
        prefab_remote.core.dir_ensure(path)
        cmd = """
        eval `ssh-agent -s`
        ssh-add $HOMEDIR/.ssh/default.rsa
        rsync -avzhe ssh %s root@%s:%s""" % (path, address, path_remote)
        prefab_base.core.execute_bash(cmd)



# def monitor(job):
#     service = job.service
#     os = service.producers['os']
#     node = os.producers['node']
#     address = node.model.data.ipPublic
#     prefab = os.executor.prefab
#     root_path = service.producers['fs'].model.data.mount
#     free_space = prefab.btrfs.getSpaceFree(root_path)




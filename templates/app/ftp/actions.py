
def init_actions_(service, args):
    # some default logic for simple actions
    return {
        'start': ['install'],
        'stop': ['install']
    }

def install(job):
    """
    Installing ftpserver
    """
    service = job.service
    prefab = service.executor.get_prefab()
    ftp_path = '/mnt/storage/'
    if not prefab.core.isLinux:
        raise RuntimeError('unfortunetly support is available for linux systems only.')
    prefab.core.sudomode = True
    prefab.package.update()
    prefab.development.python.install()
    prefab.development.pip.ensure()
    config = {}
    for space in service.producers['ftp_space']:
        if space.model.data.path.startswith('/mnt/storage/'):
            path = space.model.data.path.split("/")[-1]
        else:
            path = j.sal.fs.joinPaths(ftp_path, space.model.data.path)
        config[path] = {}
        users = space.model.data.authorizedUsers
        for user in users:
            username, passwd = user.split(":")
            config[path][username] = [passwd, space.model.data.permission]
    config_yaml = j.data.serializer.yaml.dumps(config)
    prefab.apps.pyftpserver.install(root=ftp_path, config=config_yaml)
    prefab.apps.pyftpserver.start()

def start(job):
    """
    start ftp server
    """
    service = job.service
    prefab = service.executor.get_prefab()
    prefab.apps.pyftpserver.start()

def stop(job):
    """
    stop ftp server
    """
    service = job.service
    prefab = service.executor.get_prefab()
    prefab.apps.pyftpserver.stop()
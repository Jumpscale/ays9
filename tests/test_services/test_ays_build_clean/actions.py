def init_actions_(service, args):
    """
    this needs to returns an array of actions representing the depencies between actions.
    Looks at ACTION_DEPS in this module for an example of what is expected
    """
    return {
        'install': ['init']
    }


def install(job):
    # look for build host os service
    host_os = None
    service = job.service
    for parent in service.parents:
        if parent.model.role == 'os':
            host_os = parent
            break
    else:
        raise j.exceptions.AYSNotFound("Can't find os service")

    prefab = host_os.executor.get_prefab()
    import ipdb;ipdb.set_trace
    if prefab.core.dir_exists('/mnt/building/opt')
    	prefab.core.dir_remove('/mnt/building/opt')
    dockers = ['packager', 'cockpit', 'portal', 'jumpscale', 'scality', 'geodns', 'php',
               'fs', 'grafana', 'python', 'nodejs', 'mongodb', 'golang', 'nginx', 
               'shellinabox', 'caddy', 'influxdb', 'redis']
    for docker in dockers:
    	try:
            check = prefab.core.run('docker ps -a | grep -o -F %s' %docker)
            if check[1] == docker:
               prefab.core.execute_bash('docker rm -f %s' %docker)
        except:
            continue 

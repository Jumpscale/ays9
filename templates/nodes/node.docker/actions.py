def input(job):
    r = job.service.aysrepo

    if "node" in job.model.args:
        res = job.model.args
        res["os"] = res["node"]
        res.pop("node")
        job.model.args = res

    return job.model.args


def init(job):

    r = job.service.aysrepo

    a = r.actorGet("os.ssh.ubuntu")
    if r.serviceGet("os", job.service.name, die=False) == None:
        s = a.serviceCreate(instance=job.service.name, args={
                            "node": job.service.name, "sshkey": job.service.model.data.sshkey})


def install(job):
    service = job.service
    # create the docker container based on the data
    compose = {
        'version': '2',
        'services': {
            service.name: {
                'container_name': service.name,
                'image': service.model.data.image,
                'command': service.model.data.cmd,
                'network_mode': 'bridge',
                'ports': list(service.model.data.ports),
                'volumes': list(service.model.data.volumes)
            }
        }
    }

    prefab = service.executor.get_prefab()

    base = j.sal.fs.joinPaths('/var', 'dockers', service.name)
    prefab.core.dir_ensure(base)
    prefab.package.mdupdate()
    prefab.package.ensure('python3-pip')
    prefab.development.pip.install('docker-compose')
    prefab.core.file_write(
        j.sal.fs.joinPaths(base, 'docker-compose.yml'),
        j.data.serializer.yaml.dumps(compose)
    )

    code, _, err = prefab.core.run('cd {} && docker-compose up -d'.format(base))
    if code != 0:
        raise RuntimeError('failed to provision docker container: %s' % err)

    code, docker_id, err = prefab.core.run('cd {} && docker-compose ps -q'.format(base))
    if code != 0:
        raise RuntimeError('failed to get the container id: %s' % err)
    service.model.data.id = docker_id

    # get the ipaddress and ports
    code, inspected, err = prefab.core.run('docker inspect {id}'.format(id=docker_id), showout=False)
    if code != 0:
        raise RuntimeError('failed to inspect docker %s: %s' % (service.name, err))

    inspected = j.data.serializer.json.loads(inspected)
    info = inspected[0]
    ipaddress = info['NetworkSettings']['IPAddress']
    ports = info['NetworkSettings']['Ports']

    # find parent node.
    node = None
    for parent in service.parents:
        if parent.model.role == 'node':
            node = parent

    if node is None:
        raise RuntimeError('cannot find parent node')

    docker_ports = []

    for dst_port_spec, host_port_info in ports.items():
        dst_port, _, dst_proto = dst_port_spec.partition('/')
        if host_port_info is None:
            # no bindings
            continue
        host_port = host_port_info[0]['HostPort']
        docker_ports.append('{src}:{dst}'.format(src=host_port, dst=dst_port))

    service.model.data.ipPrivate = ipaddress
    service.model.data.ipPublic = node.model.data.ipPublic
    service.model.data.sshLogin = 'root'
    service.model.data.sshPassword = 'gig1234'

    service.model.data.ports = docker_ports

    service.saveAll()


def start(job):
    service = job.service
    prefab = service.executor.get_prefab()

    docker_id = service.model.data.id
    if docker_id is None or docker_id == '':
        raise j.exceptions.RuntimeError('docker id is not known')

    prefab.core.run('docker start {id}'.format(id=docker_id))

     # get the ipaddress and ports
    code, inspected, err = prefab.core.run('docker inspect {id}'.format(id=docker_id), showout=False)
    if code != 0:
        raise RuntimeError('failed to inspect docker %s: %s' % (service.name, err))

    inspected = j.data.serializer.json.loads(inspected)
    info = inspected[0]
    ipaddress = info['NetworkSettings']['IPAddress']
    ports = info['NetworkSettings']['Ports']

    docker_ports = []
    for dst_port_spec, host_port_info in ports.items():
        dst_port, _, dst_proto = dst_port_spec.partition('/')
        if host_port_info is None:
            # no bindings
            continue
        host_port = host_port_info[0]['HostPort']
        docker_ports.append('{src}:{dst}'.format(src=host_port, dst=dst_port))

    service.model.data.ipPrivate = ipaddress
    service.model.data.ports = docker_ports

    service.saveAll()


def stop(job):
    service = job.service
    prefab = service.executor.get_prefab()

    docker_id = service.model.data.id
    if docker_id is None or docker_id == '':
        raise j.exceptions.RuntimeError('docker id is not known')

    prefab.core.run('docker stop {id}'.format(id=docker_id))


def uninstall(job):
    service = job.service
    prefab = service.executor.get_prefab()

    docker_id = service.model.data.id
    if docker_id is None or docker_id == '':
        raise j.exceptions.RuntimeError('docker id is not known')

    prefab.core.run('docker rm -f {id}'.format(id=docker_id))

    service.model.data.id = ''
    service.model.data.ipPrivate = ''
    service.model.data.ipPublic = ''
    service.model.data.sshLogin = 'root'
    service.model.data.sshPassword = 'gig1234'

    service.saveAll()

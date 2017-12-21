def install(job):
    prefab = job.service.executor.prefab
    data = job.service.model.data
    name = job.service.name

    image = job.service.producers['image_os'][0]
    image_name = image.model.data.url.split('/')[-1]

    nics = data.nics

    vm = prefab.virtualization.kvm.machines.create(
        name=name,
        os=image_name,
        disks=list(data.disks),
        nics=nics,
        memory=data.memory,
        cpucount=data.cpu,
        cloud_init=True,
        username=data.sshLogin,
        passwd=data.sshPassword,
        sshkey=None, # TODO: decide if we send a key in this level or from the os.ssh layer above this service
        start=True,
        resetPassword=False,
    )

    job.service.model.actions['uninstall'].state = 'new'
    job.service.saveAll()

    job.service.executeAction('start', inprocess=True)


def start(job):
    prefab = job.service.executor.prefab
    data = job.service.model.data
    name = job.service.name

    vm = prefab.virtualization.kvm.machines.get_by_name(name)
    vm.start()

    ip = vm.ip
    if ip is None:
        raise j.exceptions.RuntimeError("vm {} didn't receive an IP address".format(name))

    data.ipPrivate = ip
    data.ipPublic = prefab._executor.addr

    job.service.model.actions['stop'].state = 'new'

    job.service.saveAll()

def stop(job):
    prefab = job.service.executor.prefab
    data = job.service.model.data
    name = job.service.name

    vm = prefab.virtualization.kvm.machines.get_by_name(name)
    vm.stop()

    data.ipPrivate = ''
    data.ipPublic = ''

    job.service.model.actions['start'].state = 'new'

    job.service.saveAll()

def uninstall(job):
    prefab = job.service.executor.prefab
    name = job.service.name

    vm = prefab.virtualization.kvm.machines.get_by_name(name)
    if vm.is_started:
        vm.stop()
    vm.delete()

    job.service.model.data.ipPrivate = ''
    job.service.model.data.ipPublic = ''
    job.service.model.actions['install'].state = 'new'
    job.service.saveAll()

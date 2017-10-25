def install(job):
    prefab = job.service.executor.prefab
    # install kvm
    prefab.virtualization.kvm.install()
    # start libvirt-bin
    job.service.executeActionJob('start', inprocess=True)

    job.service.model.actions['uninstall'].state = 'new'
    job.service.saveAll()


def start(job):
    prefab = job.service.executor.prefab

    services_to_start = ['libvirt-bin', 'virtlogd']
    pm = prefab.system.processmanager.get()
    for service in services_to_start:
        if not pm.exists(service):
            raise j.exceptions.RuntimeError("{} service doesn't exists. \
                                             it should have been created during installation of this service".format(service))

        pm.start(service)

    job.service.model.actions['stop'].state = 'new'
    job.service.saveAll()

def stop(job):
    prefab = job.service.executor.prefab

    services_to_start = ['libvirt-bin', 'virtlogd']
    pm = prefab.system.processmanager.get()
    for service in services_to_start:
        if not pm.exists(service):
            raise j.exceptions.RuntimeError("{} service doesn't exists. \
                                             it should have been created during installation of this service".format(service))

        pm.stop(service)

    job.service.model.actions['start'].state = 'new'
    job.service.saveAll()


def uninstall(job):
    prefab = job.service.executor.prefab
    prefab.virtualization.kvm.uninstall()

    job.service.model.actions['install'].state = 'new'
    job.service.saveAll()

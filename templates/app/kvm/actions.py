def install(job):
    prefab = job.service.executor.get_prefab()
    # install kvm
    prefab.systemservices.kvm.install()
    # start libvirt-bin
    job.service.executeActionJob('start', inprocess=True)

    job.service.model.actions['uninstall'].state = 'new'
    job.service.saveAll()


def start(job):
    prefab = job.service.executor.get_prefab()

    services_to_start = ['libvirt-bin', 'virtlogd']
    for service in services_to_start:
        if not prefab.processmanager.exists(service):
            raise j.exceptions.RuntimeError("{} service doesn't exists. \
                                             it should have been created during installation of this service".format(service))

        prefab.processmanager.start(service)

    job.service.model.actions['stop'].state = 'new'
    job.service.saveAll()

def stop(job):
    prefab = job.service.executor.get_prefab()

    services_to_start = ['libvirt-bin', 'virtlogd']
    for service in services_to_start:
        if not prefab.processmanager.exists(service):
            raise j.exceptions.RuntimeError("{} service doesn't exists. \
                                             it should have been created during installation of this service".format(service))

        prefab.processmanager.stop(service)

    job.service.model.actions['start'].state = 'new'
    job.service.saveAll()


def uninstall(job):
    prefab = job.service.executor.get_prefab()
    prefab.systemservices.kvm.uninstall()

    job.service.model.actions['install'].state = 'new'
    job.service.saveAll()

def install(job):
    prefab = job.service.executor.get_prefab()
    # install openvswitch, used for kvm networking
    prefab.systemservices.openvswitch.install()
    # start openvswitch switch
    job.service.executeActionJob('start')

    job.service.model.actions['uninstall'].state = 'new'
    job.service.saveAll()

def start(job):
    prefab = job.service.executor.get_prefab()
    if not prefab.processmanager.exists('openvswitch-switch'):
        raise j.exceptions.RuntimeError("openvswitch-switch service doesn't exists. \
                                         it should have been created during installation of this service")

    prefab.processmanager.start('openvswitch-switch')

    job.service.model.actions['stop'].state = 'new'
    job.service.saveAll()

def stop(job):
    prefab = job.service.executor.get_prefab()
    if not prefab.processmanager.exists('openvswitch-switch'):
        raise j.exceptions.RuntimeError("openvswitch-switch service doesn't exists. \
                                         it should have been created during installation of this service")

    prefab.processmanager.stop('openvswitch-switch')

    job.service.model.actions['start'].state = 'new'
    job.service.saveAll()

def uninstall(job):
    prefab = job.service.executor.get_prefab()
    prefab.systemservices.openvswitch.uninstall()

    job.service.model.actions['install'].state = 'new'
    job.service.saveAll()

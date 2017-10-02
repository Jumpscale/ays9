def install(job):
    prefab = job.service.executor.prefab
    # install openvswitch, used for kvm networking
    prefab.virtualization.openvswitch.install()
    # start openvswitch switch
    job.service.executeActionJob('start')

    job.service.model.actions['uninstall'].state = 'new'
    job.service.saveAll()

def start(job):
    prefab = job.service.executor.prefab
    pm = prefab.system.processManager.get()
    if not pm.exists('openvswitch-switch'):
        raise j.exceptions.RuntimeError("openvswitch-switch service doesn't exists. \
                                         it should have been created during installation of this service")

    pm.start('openvswitch-switch')

    job.service.model.actions['stop'].state = 'new'
    job.service.saveAll()

def stop(job):
    prefab = job.service.executor.prefab
    pm = prefab.system.processManager.get()
    if not pm.exists('openvswitch-switch'):
        raise j.exceptions.RuntimeError("openvswitch-switch service doesn't exists. \
                                         it should have been created during installation of this service")

    pm.stop('openvswitch-switch')

    job.service.model.actions['start'].state = 'new'
    job.service.saveAll()

def uninstall(job):
    prefab = job.service.executor.prefab
    prefab.virtualization.openvswitch.uninstall()

    job.service.model.actions['install'].state = 'new'
    job.service.saveAll()

def install(job):
    data = job.service.model.data
    prefab = job.service.executor.prefab

    # create bridge
    if data.name not in prefab.systemservices.openvswitch.networkList():
        prefab.systemservices.openvswitch.networkCreate(data.name)
        # configure the network and the natting
        gateway = data.gateway if data.gateway else None
        prefab.system.net.netconfig(data.name, data.ipAddr, data.netmask, gateway=gateway, masquerading=data.masquerading)
        prefab.processmanager.start('systemd-networkd')

    if data.dhcpEnable:
        # add a dhcp server to the bridge
        range_start = data.dhcpRangeStart if data.dhcpRangeStart else ''
        range_stop = data.dhcpRangeStop if data.dhcpRangeStop else ''
        # if rangefrom & rangeto not specified then will serve full local range minus bottomn 10 & top 10 addr
        prefab.apps.dnsmasq.install()
        prefab.apps.dnsmasq.config(data.name, rangefrom=range_start, rangeto=range_stop)
        prefab.processmanager.restart('dnsmasq')

    job.service.model.actions['uninstall'].state = 'new'
    job.service.saveAll()

def start(job):
    prefab = job.service.executor.prefab
    if not prefab.processmanager.exists('systemd-networkd'):
        raise j.exceptions.RuntimeError("systemd-networkd service doesn't exists. \
                                         it should have been created during installation of this service")

    prefab.processmanager.start('systemd-networkd')

    job.service.model.actions['stop'].state = 'new'
    job.service.saveAll()

def stop(job):
    prefab = job.service.executor.prefab
    if not prefab.processmanager.exists('systemd-networkd'):
        raise j.exceptions.RuntimeError("systemd-networkd service doesn't exists. \
                                         it should have been created during installation of this service")

    prefab.processmanager.stop('systemd-networkd')

    job.service.model.actions['start'].state = 'new'
    job.service.saveAll()

def uninstall(job):
    data = job.service.model.data
    prefab = job.service.executor.prefab
    if data.name in prefab.systemservices.openvswitch.networkList():
        prefab.systemservices.openvswitch.networkDelete(data.name)

    job.service.model.actions['install'].state = 'new'
    job.service.saveAll()

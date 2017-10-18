def install(job):
    service = job.service
    if 'sshkey' not in service.producers:
        raise j.exceptions.AYSNotFound("No sshkey service consumed. please consume an sshkey service")

    service.logger.info("authorize ssh key to machine")
    node = service.parent

    # Looking in the parents chain is needed when we have nested nodes (like a docker node on top of an ovc node)
    # we need to find all the ports forwarding chain to reach the inner most node.
    ssh_port = '22'
    for parent in service.parents:
        if parent.model.role != 'node':
            continue
        for port in parent.model.data.ports:
            src, _, dst = port.partition(':')
            if ssh_port == dst:
                ssh_port = src
                break

    service.model.data.sshPort = int(ssh_port)

    sshkey = service.producers['sshkey'][0]
    key_path = sshkey.model.data.keyPath
    if not j.sal.fs.exists(key_path):
        raise j.exceptions.RuntimeError("sshkey path not found at %s" % key_path)
    password = node.model.data.sshPassword if node.model.data.sshPassword != '' else None
    passphrase = sshkey.model.data.keyPassphrase if sshkey.model.data.keyPassphrase != '' else None

    # used the login/password information from the node to first connect to the node and then authorize the sshkey for root
    executor = j.tools.executor.getSSHBased(addr=node.model.data.ipPublic, port=service.model.data.sshPort,
                                            login=node.model.data.sshLogin, passwd=password,
                                            allow_agent=True, look_for_keys=True, timeout=5, usecache=False,
                                            passphrase=passphrase, key_filename=key_path)
    executor.prefab.system.ssh.authorize("root", sshkey.model.data.keyPub)
    service.saveAll()


def getExecutor(job):
    service = job.service
    if 'sshkey' not in service.producers:
        raise j.exceptions.AYSNotFound("No sshkey service consumed. please consume an sshkey service")

    sshkey = service.producers['sshkey'][0]
    node = service.parent
    key_path = sshkey.model.data.keyPath
    passphrase = sshkey.model.data.keyPassphrase if sshkey.model.data.keyPassphrase != '' else None

    # search ssh port from parent node info. in case the port changed since creation of this service
    ssh_port = '22'
    for parent in service.parents:
        if parent.model.role != 'node':
            continue
        for port in parent.model.data.ports:
            src, _, dst = port.partition(':')
            if ssh_port == dst:
                ssh_port = src
                break

    executor = j.tools.executor.getSSHBased(addr=node.model.data.ipPublic, port=ssh_port,
                                            login='root', passwd=None,
                                            allow_agent=True, look_for_keys=True, timeout=5, usecache=False,
                                            passphrase=passphrase, key_filename=key_path)
    return executor

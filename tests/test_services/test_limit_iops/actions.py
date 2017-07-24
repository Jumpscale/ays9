def init_actions_(service, args):
    """
    this needs to returns an array of actions representing the depencies between actions.
    Looks at ACTION_DEPS in this module for an example of what is expected
    """
    return {
        'test': ['install']
    }


def test(job):
    import sys
    try:
        log = j.logger.get('test')
        log.addHandler(j.logger._LoggerFactory__fileRotateHandler('tests'))
        log.info('Test started')
        service = job.service
        vm_os = service.producers.get('os')[0]
        vm_exe = vm_os.executor.get_prefab()

        log.info('Install fio')
        vm_exe.core.run('apt-get update')
        vm_exe.core.run('echo "Y" | apt-get install fio')

        log.info('Run fio on vdb, iops should be less than maxIOPS')
        vm = service.producers['node'][0]
        disk = vm.producers['disk'][0]
        maxIOPS = disk.model.data.maxIOPS
        fio_cmd = "fio --ioengine=libaio --group_reporting --filename=/dev/{1} "\
                  "--runtime=30 --readwrite=randrw --size=500M --name=test{0} "\
                  "--output={0}".format('b1', 'vdb')
        vm_exe.core.run(fio_cmd)
        out = vm_exe.core.run("cat %s | grep -o 'iops=[0-9]\{1,\}' | cut -d '=' -f 2" % 'b1')
        list = out[1].split('\n')
        int_list = [int(i) for i in list if int(i) > maxIOPS]
        iops = len(int_list)
        if iops != 0:
            service.model.data.result = 'FAILED : {} {}'.format('test_limit_iops', str(sys.exc_info()[:2]))
            service.save()
            return

        log.info('Create another data disk (vdc) and set max_iops to 1000')
        vdc = vm.producers['vdc'][0]
        g8client = vdc.producers["g8client"][0]
        client = j.clients.openvcloud.getFromService(g8client)
        acc = client.account_get(vdc.model.data.account)
        space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)
        machine = space.machines[vm.name]
        disk_id = machine.add_disk(name='disk_c', description='test', size=50, type='D')
        machine.disk_limit_io(disk_id, 1000)

        log.info('Run fio on vdc, iops should be less than 1000')
        fio_cmd = "fio --ioengine=libaio --group_reporting --filename=/dev/{1} "\
                  "--runtime=30 --readwrite=randrw --size=500M --name=test{0} "\
                  "--output={0}".format('c1', 'vdc')
        vm_exe.core.run(fio_cmd)
        out = vm_exe.core.run("cat %s | grep -o 'iops=[0-9]\{1,\}' | cut -d '=' -f 2" % 'c1')
        list = out[1].split('\n')
        int_list = [int(i) for i in list if int(i) > 1000]
        iops = len(int_list)
        if iops != 0:
            service.model.data.result = 'FAILED : {} {}'.format('test_limit_iops', str(sys.exc_info()[:2]))
            service.save()
            return

        log.info('Run fio on vdc, iops should be less than 500')
        machine.disk_limit_io(disk_id, 500)
        fio_cmd = "fio --ioengine=libaio --group_reporting --filename=/dev/{1} "\
                  "--runtime=30 --readwrite=randrw --size=500M --name=test{0} "\
                  "--output={0}".format('c2', 'vdc')
        vm_exe.core.run(fio_cmd)
        out = vm_exe.core.run("cat %s | grep -o 'iops=[0-9]\{1,\}' | cut -d '=' -f 2" % 'c2')
        list = out[1].split('\n')
        int_list = [int(i) for i in list if int(i) > 500]
        iops = len(int_list)
        if iops != 0:
            service.model.data.result = 'FAILED : {} {}'.format('test_limit_iops', str(sys.exc_info()[:2]))
            service.save()
            return
        service.model.data.result = 'OK : {} '.format('test_limit_iops')
    except:
        service.model.data.result = 'ERROR : {} {}'.format('test_limit_iops', str(sys.exc_info()[:2]))
    log.info('Test Ended')
    service.save()

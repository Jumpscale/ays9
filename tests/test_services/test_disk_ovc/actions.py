def test_create(job):
    """
    Test Create Disk
    """
    import sys
    RESULT_OK = 'OK : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    RESULT_FAIL = 'FAILED : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name

    def _disk_found(disks, disk_srv):
        result = False
        for disk in disks:
            if disk['name'] == disk_srv.name and disk['descr'] == disk_srv.model.data.description:
                result = True
                break

        return result

    try:
        disk_srv = job.service.aysrepo.serviceGet(role='disk', instance=model.data.disk[0])
        client_srv = disk_srv.producers.get('g8client')[0]
        cli = j.clients.openvcloud.getFromService(client_srv)
        account = cli.account_get(name=client_srv.model.data.account, create=False)
        disks = cli.api.cloudapi.disks.list(accountId=account.id, type=disk_srv.model.data.type)
        if _disk_found(disks, disk_srv):
            model.data.result = RESULT_OK % 'Disk Created Successfully'
        else:
            model.data.result = RESULT_FAIL % 'Expected to find disk matches the test disk. Found None'
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()


def test_delete(job):
    """
    Test Delete Disk
    """
    import sys
    RESULT_OK = 'OK : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    RESULT_FAIL = 'FAILED : %s %%s' % job.service.name
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name

    def _disk_found(disks, disk_srv):
        result = False
        for disk in disks:
            if disk['name'] == disk_srv.name and disk['descr'] == disk_srv.model.data.description:
                result = True
                break

        return result

    try:
        disk_srv = job.service.aysrepo.serviceGet(role='disk', instance=model.data.disk[0])
        client_srv = disk_srv.producers.get('g8client')[0]
        cli = j.clients.openvcloud.getFromService(client_srv)
        account = cli.account_get(name=client_srv.model.data.account, create=False)
        disks = cli.api.cloudapi.disks.list(accountId=account.id, type=disk_srv.model.data.type)
        if _disk_found(disks, disk_srv):
            model.data.result = RESULT_FAIL % 'Expected not to find disk matches the test disk. Found one'
        else:
            model.data.result = RESULT_OK % 'Disk Deleted Successfully'
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()

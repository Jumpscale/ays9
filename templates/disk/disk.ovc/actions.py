def init_actions_(service, args):
    dependencies = {
        'create': ['init'],
        'limit_io': ['init'],
        'delete': ['init'],
    }
    return dependencies


def init(job):
    service = job.service
    if service.model.data.type and service.model.data.type.upper() not in ["D", "B"]:
        raise j.exceptions.Input("disk.ovc's type must be data (D) or boot (B) only")
    if 'g8client' not in service.producers:
        raise j.exceptions.AYSNotFound("no producer g8client found. cannot continue init of %s" % service)
    data = service.model.data
    if (data.maxIOPS or data.totalIopsSec) and (data.readIopsSec or data.writeIopsSec):
        raise j.exceptions.Input("total and read/write of iops_sec cannot be set at the same time")
    if (data.totalBytesSec) and (data.readBytesSec or data.writeBytesSec):
        raise j.exceptions.Input("total and read/write of bytes_sec cannot be set at the same time")
    if (data.totalBytesSecMax) and (data.readBytesSecMax or data.writeBytesSecMax):
        raise j.exceptions.Input("total and read/write of bytes_sec_max cannot be set at the same time")
    if (data.totalIopsSecMax) and (data.readIopsSecMax or data.writeIopsSecMax):
        raise j.exceptions.Input("total and read/write of iops_sec_max cannot be set at the same time")


def create(job):
    service = job.service
    g8client = service.producers["g8client"][0]
    client = j.clients.openvcloud.getFromService(g8client)
    account = client.account_get(g8client.model.data.account, create=True)
    for loc in client.locations:
        if loc['name'] == service.model.data.location:
            location = loc
            break
    else:
        raise j.exceptions.AYSNotFound("Location not found. cannot continue init of %s" % service)

    service.model.data.diskId = account.create_disk(
        name=service.model.dbobj.name,
        gid=location['gid'],
        description=service.model.data.description,
        size=service.model.data.size,
        type=service.model.data.type,
        ssd_size=service.model.data.ssdSize
    )
    service.saveAll()


def delete(job):
    service = job.service
    g8client = service.producers["g8client"][0]
    client = j.clients.openvcloud.getFromService(g8client)
    account = client.account_get(g8client.model.data.account, create=True)
    for disk in account.disks:
        if disk['id'] == service.model.data.diskId:
            break
    else:
        raise j.exceptions.AYSNotFound("Data Disk was not found. cannot continue init of %s" % service)
    account.delete_disk(service.model.data.diskId)


def processChange(job):
    service = job.service
    args = job.model.args
    category = args.pop('changeCategory')
    if category == "dataschema":
        for key, value in args.items():
            if key not in ['size', 'type', 'description', 'devicename', 'ssdSize', 'g8client', 'location']:
                setattr(service.model.data, key, value)
        if service.aysrepo.servicesFind(actor='node.ovc'):
            service.executeAction('limit_io')


def limit_io(job):
    service = job.service
    g8client = service.producers["g8client"][0]
    data = service.model.data
    client = j.clients.openvcloud.getFromService(g8client)
    account = client.account_get(g8client.model.data.account, create=True)
    for disk in account.disks:
        if disk['id'] == service.model.data.diskId:
            break
    else:
        raise j.exceptions.AYSNotFound("Data Disk was not found. cannot continue init of %s" % service)
    client.api.cloudapi.disks.limitIO(diskId=data.diskId, iops=data.maxIOPS, total_bytes_sec=data.totalBytesSec,
                                      read_bytes_sec=data.readBytesSec, write_bytes_sec=data.writeBytesSec, total_iops_sec=data.totalIopsSec,
                                      read_iops_sec=data.readIopsSec, write_iops_sec=data.writeIopsSec,
                                      total_bytes_sec_max=data.totalBytesSecMax, read_bytes_sec_max=data.readBytesSecMax,
                                      write_bytes_sec_max=data.writeBytesSecMax, total_iops_sec_max=data.totalIopsSecMax,
                                      read_iops_sec_max=data.readIopsSecMax, write_iops_sec_max=data.writeIopsSecMax,
                                      size_iops_sec=data.sizeIopsSec)

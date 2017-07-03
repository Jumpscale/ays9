def init(job):
    service = job.service
    repo = service.aysrepo
    disksizes = list(service.model.data.datadisks)
    disks = []
    for idx, size in enumerate(disksizes):
        disk_name = 'disk-%s' % idx
        repo.actorGet('disk.ovc').serviceCreate(disk_name, {'size': size})
        disks.append(disk_name)

    # ovc node.
    vm = {
        'os.image': 'Ubuntu 16.04 x64',
        'bootdisk.size': 10,
        'vdc': service.parent.name,
        'memory': 4,
        'ports': [
            '2200:22',
            '2201:2201',
            '2202:2202',
            '2203:2203',
            '80:80'
        ],
        'disk': disks
    }
    nodevm = repo.actorGet('node.ovc').serviceCreate(service.name, vm)
    service.consume(nodevm)  # CONSUME NODEVM TO FIX ORDER OF EXECUTION

    repo.actorGet('os.ssh.ubuntu').serviceCreate(service.name, {'node': service.name})
    repo.actorGet('app_docker').serviceCreate('appdocker', {'os': service.name})

    # filesystem
    # 1- fuse
    fuse_cfg = {
        'mount.namespace': 'aysbuild',
        'mount.mountpoint': '/opt',
        'mount.flist':'https://stor.jumpscale.org/stor2/flist/aysbuild/jumpscale.flist',
        'mount.mode': 'ol',
        'mount.trimbase': True,
        'mount.trim': '/opt',
        'backend.path': '/mnt/fs_backend/opt',
        'backend.namespace': 'aysbuild',
        'backend.cleanup.cron': "@every 1h",
        'backend.cleanup.old': 24,
        'store.url': 'https://stor.jumpscale.org/stor2'
    }

    repo.actorGet('vfs_config').serviceCreate('opt', fuse_cfg)

    fuse = {
        'os': service.name,
        'vfs_config': ['opt']
    }

    repo.actorGet('fs.g8osfs').serviceCreate('fuse', fuse)

    # 2- btrfs
    btrfs = {
        'os': service.name,
        'mount': '/data'
    }

    repo.actorGet('fs.btrfs').serviceCreate('data', btrfs)

    # tidb docker
    tidb = {
        'image': 'jumpscale/ubuntu1604',
        'hostname': service.model.data.fqdn,
        'fs': ['fuse'],
        'os': service.name,
        'ports': [
            '2201:22',
            '3306:3306'
        ],
        'volumes': [
            '/opt/:/opt/',
        ]
    }

    repo.actorGet('node.docker').serviceCreate('tidb', tidb)
    repo.actorGet('os.ssh.ubuntu').serviceCreate('tidb', {'node': 'tidb'})

    # app docker
    owncloud = {
        'image': 'jumpscale/ubuntu1604',
        'hostname': service.model.data.fqdn,
        'fs': ['fuse', 'data'],
        'os': service.name,
        'ports': [
            '2202:22',
            '8000:80'
        ],
        'volumes': [
            '/opt/:/opt/',
            '/data/:/data/',
        ]
    }

    repo.actorGet('node.docker').serviceCreate('owncloud', owncloud)
    repo.actorGet('os.ssh.ubuntu').serviceCreate('owncloud', {'node': 'owncloud'})

    repo.actorGet('tidb').serviceCreate('tidb', {'os': 'tidb', 'clusterId': '1'})

    # # app
    # machineip = nodevm.model.data.ipPublic
    # # ip2num
    # machineuniquenumber = j.sal.nettools.ip_to_num(machineip)
    # domain = "{appname}-{num}.gigapps.io".format(appname=service.model.data.hostprefix, num=machineuniquenumber)
    #service.model.data.fqdn = fqdn
    #service.saveAll()

    owncloudconf = {
        'os': 'owncloud',
        'tidb': 'tidb',
        'tidbuser': 'root',
        'tidbpassword': '',
        'sitename': service.model.data.fqdn,
        'owncloudAdminUser': 'admin',
        'owncloudAdminPassword': 'admin'
    }

    repo.actorGet('owncloud').serviceCreate('own1', owncloudconf)

    # caddy proxy
    caddy = {
        'image': 'jumpscale/ubuntu1604',
        'docker': 'docker',
        'hostname': 'caddy',
        'fs': ['fuse'],
        'os': service.name,
        'ports': [
            '2203:22',
            '80:80'
        ],
        'volumes': [
            '/opt/:/opt/',
        ]
    }

    repo.actorGet('node.docker').serviceCreate('caddy', caddy)
    repo.actorGet('os.ssh.ubuntu').serviceCreate('caddy', {'node': 'caddy'})

    proxy = {
        'src': '/',
        'dst': ['172.17.0.1:8000'],
        'transparent': True,

    }

    repo.actorGet('caddy_proxy').serviceCreate('proxy', proxy)

    caddy_service = {
        'os': 'caddy',
        'fs': 'cockpit',
        'email': 'mail@fake.com',
        'hostname': ':80',
        'caddy_proxy': ['proxy'],
        'stagging': True,
    }

    repo.actorGet('caddy').serviceCreate('caddy', caddy_service)



def install(job):

    service = job.service
    repo = service.aysrepo
    nodevm = repo.serviceGet(role='node.ovc', instance=service.name)   # nodevm.
    # app
    machineip = nodevm.model.data.ipPublic
    # ip2num
    machineuniquenumber = j.sal.nettools.ip_to_num(machineip)
    fqdn = service.model.data.fqdn
    if not fqdn:
        fqdn = "{appname}-{num}.gigapps.io".format(appname=service.model.data.hostprefix, num=machineuniquenumber)

    httpdomain = "http://{fqdn}".format(fqdn=fqdn)
    if service.model.data.enablehttps is False:
        httpdomain = httpdomain.replace("https", "http")
    else:
        httpdomain = httpdomain.replace("https", "https")

    service.model.data.fqdn = fqdn
    service.saveAll()

    # NOW SET the domain on the services that requires the fqdn.

    # 1- owncloud service conf
    owncloudconf = repo.serviceGet(role="owncloud", instance="own1")
    owncloudconf.model.data.sitename = fqdn
    owncloudconf.saveAll()

#    # 2- caddy service conf
    caddyconf = repo.serviceGet(role='caddy', instance='caddy')
    caddyconf.model.data.hostname = httpdomain
    caddyconf.saveAll()

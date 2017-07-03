def input(job):
    service = job.service
    repo = service.aysrepo
    if job.model.args.get('vdc', '') == '':
        g8clients = repo.servicesFind(actor='g8client')
        if g8clients:
            g8client = g8clients[0]
            cl = j.clients.openvcloud.getFromService(g8client)
            if cl.locations:
                location = cl.locations[0]['name']
            else:
                raise j.exceptions.Input('this g8client has no locations associated to it')
            vdc_info = {
                'location': location,
                'g8client': g8client.model.name,
            }

            vdc = repo.actorGet('vdc').serviceCreate(service.name, vdc_info)
            args = job.model.args
            args['vdc'] = service.name
            return args
        else:
            raise j.exceptions.Input("can not create vdc for you, if there is no any g8clients" % service)


def init(job):
    service = job.service
    repo = service.aysrepo

    # ovc node.
    vm = {
        'os.image': service.model.data.image,
        'bootdisk.size': 10,
        'vdc': service.parent.name,
        'memory': 4,
        'ports': [
            '2200:22',
            '2201:2201',
            '2202:2202',
            '80:80'
        ],
        'disk': list(service.model.data.disk)
    }

    nodevm = repo.actorGet('node.ovc').serviceCreate(service.name, vm)
    repo.actorGet('os.ssh.ubuntu').serviceCreate(service.name, {'node': nodevm.name})
    service.consume(nodevm)  # CONSUME NODEVM TO FIX ORDER OF EXECUTION

    # filesystem
    # 1- fuse
    fuse_cfg = {
        'mount.namespace': 'sandbox_ub1604',
        'mount.mountpoint': '/mnt/fs',
        'mount.flist': 'https://stor.jumpscale.org/stor2/flist/sandbox_ub1604/opt.flist',
        'mount.mode': 'ol',
        'mount.trimbase': False,
        'backend.path': '/mnt/fs_backend/opt',
        'backend.namespace': 'sandbox_ub1604',
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
    repo.actorGet('app_docker').serviceCreate('docker')


    # app docker
    docker = {
        'image': 'jumpscale/ubuntu1604',
        'docker': 'docker',
        'hostname': service.model.data.fqdn,
        'fs': ['fuse', 'data'],
        'os': service.name,
        'ports': [
            '2201:22',
            '8000:8000'
        ],
        'volumes': [
            '/mnt/fs/opt/:/opt/',
            '/data:/data'
        ]
    }

    repo.actorGet('node.docker').serviceCreate('app', docker)
    repo.actorGet('os.ssh.ubuntu').serviceCreate('app', {'node': 'app'})


    app = {
        'os': 'app',
        'domain': service.model.data.fqdn,
        'storage.data': '/data/data',
        'storage.meta': '/data/meta',
        'key.access': service.model.data.keyAccess,
        'key.secret': service.model.data.keySecret,
    }

    repo.actorGet('scality').serviceCreate('app', app)

    # caddy proxy
    caddy = {
        'image': 'jumpscale/ubuntu1604',
        'docker': 'docker',
        'hostname': 'caddy',
        'fs': ['fuse'],
        'os': service.name,
        'ports': [
            '2202:22',
            '80:80'
        ],
        'volumes': [
            '/mnt/fs/opt/:/opt/',
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

    # 1- scality service conf
    scalityconf = repo.serviceGet(role="scality", instance="app")
    scalityconf.model.data.domain = fqdn
    scalityconf.saveAll()

    # 2- caddy service conf
    caddyconf = repo.serviceGet(role='caddy', instance='caddy')
    caddyconf.model.data.hostname = httpdomain
    caddyconf.saveAll()

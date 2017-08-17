def init(job):
    service = job.service
    repo = service.aysrepo

    node = service.aysrepo.servicesFind(actor='node.*', name=service.model.data.hostNode)[0]
    os = service.aysrepo.servicesFind(actor='os.*', name=service.model.data.hostNode)[0]

    # filesystem
    # 1- fuse
    fuse_cfg = {
        'mount.namespace': 'sandbox_ub1604',
        'mount.mountpoint': '/opt',
        'mount.flist': service.model.data.flist,
        'mount.mode': 'ol',
        'mount.trimbase': True,
        'mount.trim': '/opt',
        'backend.path': '/mnt/fs_backend/opt',
        'backend.namespace': 'aysbuild',
        'backend.cleanup.cron': "@every 1h",
        'backend.cleanup.old': 24,
        'store.url': 'https://stor.jumpscale.org/stor2'
    }

    vfs_config = repo.actorGet('vfs_config').serviceCreate('opt', fuse_cfg)

    fuse = {
        'os': os.name,
        'vfs_config': [vfs_config.name]
    }

    fs = repo.actorGet('fs.g8osfs').serviceCreate('fuse', fuse)
    service.consume(fs)

    dns_sshkey = service.aysrepo.servicesFind(actor='sshkey', name=service.model.data.dnsSshkey)[0]
    dns_clients_names = []
    for i, addr in enumerate(['dns1.aydo.com', 'dns2.aydo.com', 'dns3.aydo.com']):
        name = "dns%s" % (i + 1)
        dns_clients_names.append(name)
        dns = {
            'addr': addr,
            'port': 32768,
            'sshkey': dns_sshkey.name,
            'login': 'root',
        }
        repo.actorGet('dnsclient').serviceCreate(name, dns)
    if service.model.data.domain:
        # only take that last part of the domain.
        # e.g: sub.domain.com -> we keep domain.com
        root_domain = '.'.join(service.model.data.domain.split('.')[-2:])
        # sub domain is the domain minus the root_domain
        subdomain = sub = service.model.data.domain[:-len(root_domain) - 1]
        dns_domain = {
            'dnsclient': dns_clients_names,
            'ttl': 600,
            'domain': root_domain,
            'a.records': ["{subdomain}:{node}".format(subdomain=subdomain, node=node.name)],
            'node': [node.name],
        }

        dns_domain_service = repo.actorGet('dns_domain').serviceCreate('cockpit', dns_domain)
        service.consume(dns_domain_service)

    api = {
        'src': '/api',
        'dst': ['127.0.0.1:5000'],
        'without': '/api'
    }

    repo.actorGet('caddy_proxy').serviceCreate('10_api', api)

    api = {
        'src': '/',
        'dst': ['127.0.0.1:82']
    }

    repo.actorGet('caddy_proxy').serviceCreate('99_portal', api)

    api = {
        'src': '/ays_bot/',
        'dst': ['127.0.0.1:6366']
    }

    repo.actorGet('caddy_proxy').serviceCreate('88_aysbot', api)

    caddy_cfg = {
        'os': os.name,
        'fs': fs.name,
        'email': service.model.data.caddyEmail,
        'hostname': service.model.data.domain,
        'caddy_proxy': ['10_api', '99_portal'],
        'stagging': service.model.data.caddyStagging
    }

    caddy = repo.actorGet('caddy').serviceCreate('main', caddy_cfg)
    service.consume(caddy)

    mongodb_cfg = {
        'os': os.name,
        'fs': fs.name,
    }

    mongodb = repo.actorGet('mongodb').serviceCreate('main', mongodb_cfg)
    service.consume(mongodb)

    redis_cfg = {
        'os': os.name,
        'fs': fs.name,
        'unixsocket': '/optvar/tmp/redis.sock',
        'maxram': 20000000,
        'appendonly': True,
    }

    redis = repo.actorGet('redis').serviceCreate('ays', redis_cfg)
    service.consume(redis)

    portal_cfg = {
        'os': os.name,
        'fs': fs.name,
        'redis': redis.name,
        'oauth.enabled': True,
        'oauth.client_id': service.model.data.oauthClientId,
        'oauth.scope': 'user:email:main,user:memberof:{organization}'.format(organization=service.model.data.oauthOrganization),
        'oauth.secret': service.model.data.oauthClientSecret,
        'oauth.client_url': 'https://itsyou.online/v1/oauth/authorize',
        'oauth.client_user_info_url': 'https://itsyou.online/api/users',
        'oauth.provider': 'itsyou.online',
        'oauth.default_groups': ['admin', 'user'],
        'oauth.organization': service.model.data.oauthOrganization,
        'oauth.redirect_url': "https://{domain}/restmachine/system/oauth/authorize".format(domain=service.model.data.domain),
        'oauth.token_url': 'https://itsyou.online/v1/oauth/access_token'
    }

    portal = repo.actorGet('portal').serviceCreate('main', portal_cfg)
    service.consume(portal)

    ayscockpit_cfg = {
        'os': os.name,
        'fs': fs.name,
        'redis': redis.name,
        'portal': portal.name,

        'domain': service.model.data.domain,

        'oauth.client_secret': service.model.data.oauthClientSecret,
        'oauth.client_id': service.model.data.oauthClientId,
        'oauth.organization': service.model.data.oauthOrganization,
        'oauth.jwt_key': service.model.data.oauthJwtKey,
        'oauth.redirect_url': 'https://{domain}/api/oauth/callback'.format(domain=service.model.data.domain),

        'api.host': '127.0.0.1',
        'api.port': 5000,
    }

    ayscockpit = repo.actorGet('ayscockpit').serviceCreate('main', ayscockpit_cfg)
    service.consume(ayscockpit)
    # # write the init script that will be used in case of machine shutdown
    #
    # os = service.aysrepo.servicesFind(actor='os.*', name=service.model.data.hostNode)[0]
    # vm_prefab = os.executor.get_prefab()
    # rc_local = vm_prefab.core.file_read('/etc/rc.local').split('\n')
    # for idx, line in enumerate(rc_local):
    #     if line == 'exit 0':
    #         rc_local.insert(idx, 'bash /etc/startup.sh')
    #         rc_local.insert(idx, 'export HOME=/root')
    #         break
    # vm_prefab.core.file_write('/etc/rc.local', '\n'.join(rc_local))



    # client_id = service.model.data.oauthClientId
    # if not service.model.data.oauthClientId:
    #     client_id = service.model.data.botClient
    # aysbot_cfg = {
    #     'os': os.name,
    #     'fs': fs.name,
    #     'oauth.secret': service.model.data.botSecret,
    #     'oauth.client': client_id,
    #     'oauth.redirect': 'https://{domain}/ays_bot/callback'.format(domain=service.model.data.domain),
    #     'oauth.host': '0.0.0.0',
    #     'oauth.port': 6366,
    # }
    #
    # aysbot = repo.actorGet('aysbot').serviceCreate('main', aysbot_cfg)
    # service.consume(aysbot)


def update(job):
    service = job.service
    prefab = service.executor.get_prefab()

    dependencies = ['caddy', 'mongodb', 'redis', 'portal', 'ayscockpit']
    service.logger.info('stop all dependencies')
    for dep in dependencies:
        s = service.aysrepo.servicesFind(actor=dep)[0]
        job = s.getJob('stop')
        job.executeInProcess()

    fs = service.aysrepo.serviceGet('fs.g8osfs', 'fuse')
    job = fs.getJob('stop')
    job.executeInProcess()

    os = service.aysrepo.servicesFind(actor='os.*', name=service.model.data.hostNode)[0]
    vm_prefab = os.executor.get_prefab()

    service.logger.info('remove fs backend')
    vfs_config = service.aysrepo.serviceGet('vfs_config', 'opt')
    vm_prefab.core.dir_remove(vfs_config.model.data.backendPath, recursive=True)

    service.logger.info('restart fuse')
    job = fs.getJob('start')
    job.executeInProcess()

    service.logger.info('restart dependencies')
    for dep in dependencies:
        s = service.aysrepo.servicesFind(actor=dep)[0]
        job = s.getJob('start')
        job.executeInProcess()

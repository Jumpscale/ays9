def install(job):
    service = job.service
    prefab = job.service.executor.prefab

    name = "caddy_%s" % service.name
    proxies_dir = prefab.core.replace('$JSCFGDIR/caddy/%s/proxies' % name)
    prefab.core.dir_ensure(proxies_dir)

    for proxy_info in service.producers.get('caddy_proxy', []):
        dst = ' '.join(proxy_info.model.data.dst)
        cfg = 'proxy %s %s {\n' % (proxy_info.model.data.src, dst)
        cfg += '\tfail_timeout %s\n' % proxy_info.model.data.failTimeout
        cfg += '\tmax_fails %s\n' % proxy_info.model.data.maxFails
        if proxy_info.model.data.without != '':
            cfg += '\twithout %s\n' % proxy_info.model.data.without
        for header in proxy_info.model.data.headerUpstream:
            cfg += '\theader_upstream %s\n' % header
        for header in proxy_info.model.data.headerDownstream:
            cfg += '\theader_downstream %s\n' % header
        if proxy_info.model.data.transparent is True:
            cfg += '\ttransparent\n'
        cfg += '}\n'

        prefab.core.file_write(proxies_dir + '/%s' % proxy_info.name, cfg)

    cfg = ''
    if not service.model.data.hostname:
        node = service.aysrepo.servicesFind(actor='node.*')[0]
        service.model.data.hostname = node.model.data.ipPublic
    cfg += service.model.data.hostname + '\n'
    if service.model.data.gzip:
        cfg += 'gzip\n'
    cfg += 'import %s/*\n' % proxies_dir

    conf_location = prefab.core.replace('$JSCFGDIR/caddy/%s/Caddyfile' % name)
    prefab.core.file_write(conf_location, cfg)

    #bin_location = prefab.core.command_location('caddy')
    # FORCE TO USE NEW VERSION OF CADDY
    caddy_url = 'https://github.com/mholt/caddy/releases/download/v0.9.4/caddy_linux_amd64.tar.gz'
    dest = '$tmpDir/caddy_linux_amd64.tar.gz'
    prefab.core.file_download(caddy_url, dest)
    prefab.core.run('cd $tmpDir && tar xvf $tmpDir/caddy_linux_amd64.tar.gz && mv $tmpDir/caddy_linux_amd64 /root/caddybin')
    bin_location = prefab.core.replace('/root/caddybin')
    cmd = '{bin} -conf {conf} --agree --email {email}'.format(
        bin=bin_location,
        conf=conf_location,
        email=service.model.data.email)
    if service.model.data.stagging is True:
        # enable stating environment, remove for prodction
        cmd += ' -ca https://acme-staging.api.letsencrypt.org/directory'
    pm = prefab.system.processmanager.get()
    pm.ensure("caddy_%s" % service.name, cmd=cmd, path='$JSCFGDIR/caddy/%s' % name, autostart=True)


def start(job):
    prefab = job.service.executor.prefab
    pm = prefab.system.processmanager.get()pm =
    pm.start("caddy_%s" % job.service.name)


def stop(job):
    prefab = job.service.executor.prefab
    pm = prefab.system.processmanager.get()
    pm.stop("caddy_%s" % job.service.name)

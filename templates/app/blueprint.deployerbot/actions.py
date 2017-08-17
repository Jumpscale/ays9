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

    redis_cfg = {
        'os': os.name,
        'fs': fs.name,
        'unixsocket': '/optvar/tmp/redis.sock',
        'maxram': 2000000,
        'appendonly': True,
    }

    redis = repo.actorGet('redis').serviceCreate('ays', redis_cfg)


    # service = job.service
    # prefab = service.executor.get_prefab()
    # args = service.model.data

    # # Install dependencies
    # prefab.development.js8.install()
    # prefab.apps.redis.build(reset=True)
    # prefab.apps.redis.start(maxram="200mb")
    # prefab.solutions.cockpit.install_deps()

    # # Configure ays
    # AYS_CONFIG_LOCATION = "$JSCFGDIR/ays/ays.conf"
    # _conf = {
    #     "redis": {
    #         "host": "localhost",
    #         "port": 6379,
    #     },
    #     "metadata": {
    #         "jumpscale": {
    #             "url": "https://github.com/Jumpscale/ays_jumpscale8",
    #             "branch": "master"
    #         }
    #     }
    # }

    # ays_conf = yaml.dump(_conf, default_flow_style=False)
    # prefab.core.dir_ensure(os.path.dirname(AYS_CONFIG_LOCATION))
    # prefab.core.file_write(location=AYS_CONFIG_LOCATION, content=ays_conf, replaceArgs=True)
    # pm = prefab.processmanager.get("tmux")
    # pm.ensure(name="ays_daemon", cmd="ays start")

    # prefab.development.git.pullRepo('https://github.com/Jumpscale/jscockpit', '$CODEDIR/github/jumpscale/jscockpit')

    # # Prepare ssh keys
    # dns = service.producers['sshkey'][0]
    # DNS_PATH = '/root/.ssh/dns_rsa'
    # prefab.core.file_write(location=DNS_PATH,
    #                         content=dns.model.data.keyPriv,
    #                         mode=600)
    # prefab.core.run("ssh-keygen -y -f {dns_path} > {dns_path}.pub".format(dns_path=DNS_PATH))

    # # Prepare the conifg.yaml
    # g8_options = {}
    # for option in args.g8:
    #     key_address = option.split('|', 1)
    #     g8_options[key_address[0]] = {"address": key_address[1]}

    # deployer_cfg = {
    #     "bot": {
    #         "token": args.botToken
    #     },
    #     "g8": g8_options,
    #     "oauth": {
    #         "port": args.oauthPort,
    #         "itsyouonlinehost": args.oauthItsyouonlinehost,
    #         "client_id": args.oauthClient,
    #         "host": args.oauthHost,
    #         "client_secret": args.oauthSecret,
    #         "redirect_uri": args.oauthRedirect,
    #     },
    #     "dns": {
    #         "sshkey": DNS_PATH,
    #     }
    # }
    # deployer_cfg = yaml.dump(deployer_cfg, default_flow_style=False)
    # prefab.core.file_write(location="$CODEDIR/github/jumpscale/jscockpit/deployer_bot/config.yaml",
    #                         content=deployer_cfg,
    #                         replaceArgs=True)

    # cmd = "cd $CODEDIR/github/jumpscale/jscockpit/deployer_bot && ./telegram-bot -c config.yaml"
    # pm.ensure(name="deployer", cmd=cmd)

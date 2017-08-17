def install(job):
    service = job.service
    prefab = job.service.executor.get_prefab()

    cfg = {'token': service.model.data.botToken,
           'oauth': {
               'host': service.model.data.oauthHost,
               'port': service.model.data.oauthPort,
               'organization': service.model.data.oauthClient,
               'client_id': service.model.data.oauthClient,
               'client_secret': service.model.data.oauthSecret,
               'redirect_uri': service.model.data.oauthRedirect,
               'itsyouonlinehost': service.model.data.oauthItsyouonlinehost
               }
           }
    prefab.apps.aysbot.create_config(cfg=cfg)
    prefab.apps.aysbot.install()

def start(job):
    prefab = job.service.executor.get_prefab()
    prefab.processmanager.start('aysbot__main')


def stop(job):
    prefab = job.service.executor.get_prefab()
    prefab.processmanager.stop('aysbot__main')

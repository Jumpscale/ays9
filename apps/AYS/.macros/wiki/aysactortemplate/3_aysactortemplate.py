from collections import OrderedDict


def main(j, args, params, tags, tasklet):
    name = args.getTag('aysname')
    reponame = args.getTag('reponame') or None
    ctx = args.requestContext

    try:
        aysactor = j.apps.actorsloader.getActor('ays', 'tools')
        client = aysactor.get_client(ctx=ctx)
        if not reponame:
            # FIXME: migrate to ays_api calls if not reponame.
            # template = j.atyourservice.server.actorTemplates[name]
            template = client.getAYSTemplate(name).json()
            services = []
        else:
            template = client.getTemplate(name, reponame).json()
            services = client.listServices(reponame).json()
        if template:
            info = {}
            code_bloks = {
                'action': template['action'],
                'config.yaml': '\n'+j.data.serializer.yaml.dumps(template['config']),
                'schema.capnp': template['schema']
            }
            info = OrderedDict(sorted(info.items()))
            args.doc.applyTemplate({'data': info, 'services': services, 'code_bloks': code_bloks,
                                    'template_name': name, 'reponame': reponame if reponame else '',
                                    })
        else:
            args.doc.applyTemplate({'error': 'template does not exist'})
    except:
        args.doc.applyTemplate({'error': e.__str__()})


    params.result = (args.doc, args.doc)
    return params

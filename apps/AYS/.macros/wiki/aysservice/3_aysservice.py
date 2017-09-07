from collections import OrderedDict


def main(j, args, params, tags, tasklet):
    try:
        role = args.getTag('aysrole')
        name = args.getTag('aysname')
        reponame = args.getTag('reponame')

        ctx = args.requestContext
        aysactor = j.apps.actorsloader.getActor('ays', 'tools')
        client = aysactor.get_client(ctx=ctx)
        service = client.getServiceByName(name, role, reponame).json()
        if service:
            link_to_template = ('[%s|ActorTemplate?aysname=%s&reponame=%s]' % (role, role, reponame))
            link_to_repo = ('[%s|Repo?reponame=%s]' % (reponame, reponame))
            # we prepend service path with '$codedir' to make it work in the explorer.
            # because of this line :
            # https://github.com/Jumpscale/jumpscale_portal8/blob/master/apps/portalbase/macros/page/explorer/1_main.py#L25

            hidden = ['key.priv', 'consumers', 'producers', 'children', 'actions', 'password', 'passwd', 'pwd', 'oauth.jwt_key', 'keyPriv', 'repository']
            data_revised = dict()
            for k, v in service.items():
                if k.strip() in hidden:
                    continue
                else:
                    if k == "path":
                        data_revised[k] = v.replace("!", "\!")  # don't render paths as images in .wiki pages.
                    else:
                        data_revised[k] = v.replace('\\n', '') if isinstance(v, str) else v
            # Remove duplicate services from producers and consumers
            producers = [dict(p) for p in set([tuple(pr.items()) for pr in service['producers']])]
            consumers = [dict(c) for c in set([tuple(co.items()) for co in service['consumers']])]
            extra_data = {'producers': producers, 'consumers': consumers, 'actions': service['actions'], 'children': service['children']}
            args.doc.applyTemplate({
                'service': service,
                'type': link_to_template,
                'extra_data': extra_data,
                'data': data_revised,
                'name': name,
                'role': role,
                'reponame': link_to_repo,
            })

        else:
            args.doc.applyTemplate({'error': 'service not found'})

    except Exception as e:
        args.doc.applyTemplate({'error': e.__str__()})

    params.result = (args.doc, args.doc)
    return params

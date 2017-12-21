def main(j, args, params, tags, tasklet):
    def alphabetical(bp):
        return bp.name
    try:
        ctx = args.requestContext
        aysactor = j.apps.actorsloader.getActor('ays', 'tools')
        client = aysactor.get_client(ctx=ctx)
        reponame = args.getTag('reponame')

        blueprints = None
        blueprints = client.listBlueprints(reponame).json()

        bps = list()

        for blprint in blueprints:
            blueprint = client.getBlueprint(blprint['name'], reponame).json()
            bp = dict()
            if blueprint['archived']:
                label_color = 'warning'
                label_content = 'archived'
                icon = 'saved'

            # elif not blueprint.is_valid:
            #     label_color = 'danger'
            #     label_content = 'error'
            #     icon = 'remove'

            else:
                label_color = 'success'
                label_content = 'active'
                icon = 'ok'

            bp['title'] = blueprint['name']
            bp['label_content'] = label_content
            bp['icon'] = icon
            bp['label_color'] = label_color
            bp['content'] = j.portal.tools.html.htmlfactory.escape(blueprint['content'].replace('\n', '\?'))
            bps.append({blueprint['name']: bp})
        args.doc.applyTemplate({'data': bps, 'reponame': reponame})

    except Exception as e:
        args.doc.applyTemplate({'error': e.__str__()})

    params.result = (args.doc, args.doc)
    return params

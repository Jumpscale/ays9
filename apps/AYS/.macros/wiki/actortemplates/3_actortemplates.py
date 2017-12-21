

def main(j, args, params, tags, tasklet):
    doc = args.doc
    reponame = args.getTag('reponame') or None

    ctx = args.requestContext
    aysactor = j.apps.actorsloader.getActor('ays', 'tools')
    client = aysactor.get_client(ctx=ctx)
    try:
        if reponame:
            templates = client.listTemplates(repository=reponame).json()
            args.doc.applyTemplate({'templates': templates, 'reponame': reponame})
        else:
            templates = client.listAYSTemplates().json()
            args.doc.applyTemplate({'templates': templates})
    except Exception as e:
        args.doc.applyTemplate({'error': str(e)})

    params.result = (doc, doc)

    return params

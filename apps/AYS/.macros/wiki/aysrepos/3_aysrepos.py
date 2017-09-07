

def main(j, args, params, tags, tasklet):
    try:
        ctx = args.requestContext
        aysactor = j.apps.actorsloader.getActor('ays', 'tools')
        client = aysactor.get_client(ctx=ctx)
        res = client.listRepositories()
        repos = res.json()
        args.doc.applyTemplate({'repos': repos})
    except Exception as e:
        args.doc.applyTemplate({'error': str(e)})

    params.result = (args.doc, args.doc)
    return params

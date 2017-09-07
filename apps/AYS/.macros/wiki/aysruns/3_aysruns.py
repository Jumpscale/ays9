

def main(j, args, params, tags, tasklet):
    try:
        reponame = args.getTag('reponame')

        ctx = args.requestContext
        aysactor = j.apps.actorsloader.getActor('ays', 'tools')
        client = aysactor.get_client(ctx=ctx)

        runs = client.listRuns(reponame).json()
        if runs:
            args.doc.applyTemplate({'runs': runs, 'reponame': reponame})
        else:
            args.doc.applyTemplate({'error': 'No runs on this repo', 'reponame': reponame})

    except Exception as e:
        args.doc.applyTemplate({'error': e.__str__()})

    params.result = (args.doc, args.doc)
    return params

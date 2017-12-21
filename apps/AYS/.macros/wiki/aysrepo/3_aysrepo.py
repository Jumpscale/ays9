import requests

def main(j, args, params, tags, tasklet):
    try:
        ctx = args.requestContext
        aysactor = j.apps.actorsloader.getActor('ays', 'tools')
        client = aysactor.get_client(ctx=ctx)

        reponame = args.getTag('reponame')
        repo = client.getRepository(reponame).json()
        args.doc.applyTemplate({'repo': repo})
        params.result = (args.doc, args.doc)

    except requests.exceptions.HTTPError as e:
        err = "%s" % e.response.json()['error']
        args.doc.applyTemplate({'error': err})
        params.result = (args.doc, args.doc)

    except Exception as e:
        args.doc.applyTemplate({'error': str(e)})
        params.result = (args.doc, args.doc)
    return params

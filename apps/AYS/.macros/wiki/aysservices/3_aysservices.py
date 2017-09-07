
def svkey(sv):
    return sv['role'] + "!" + sv['name']


def svdetailslink(sv):
    return "Service?aysrole={}&aysname={}&reponame={}".format(sv['role'], sv['name'], sv['repository'])


def flatToTree(servicesdict):
    """
    Takes in a flat services dict and outputs a structured tree to be rendered by bootstrap-treeview.

    @param servicesdict dict: servicekey mapped to servicename

    @returns tree services.

    """

    processed = set()

    def processService(key):
        service = servicesdict[key]
        processed.add(key)
        children = []
        for c in service.get('children', []):
            children.append(servicesdict[svkey(c)])

        data = {'text': key, 'href': svdetailslink(service), 'nodes': [processService(svkey(c)) for c in children]}

        return data

    tree = []

    for key, service in servicesdict.items():
        if key not in processed:
            tree.append(processService(key))
    return tree


def main(j, args, params, tags, tasklet):
    try:
        reponame = args.getTag('reponame') or ''
        ctx = args.requestContext
        aysactor = j.apps.actorsloader.getActor('ays', 'tools')
        client = aysactor.get_client(ctx=ctx)

        services = client.listServices(reponame).json()
        fullservicesinfo = {}
        for s in services:
            name, role = s['name'], s['role']
            fullservicesinfo[svkey(s)] = (client.getServiceByName(name, role, reponame).json())
        servicestree = flatToTree(fullservicesinfo)
        args.doc.applyTemplate({'services': services, 'reponame': reponame, 'servicestree': servicestree})

    except Exception as e:
        args.doc.applyTemplate({'error': str(e)})

    params.result = (args.doc, args.doc)

    return params

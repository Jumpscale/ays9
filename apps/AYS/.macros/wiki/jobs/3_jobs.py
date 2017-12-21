
def main(j, args, params, tags, tasklet):
    page = args.page
    jobs = j.data.serializer.yaml.loads(args.cmdstr)['jobs']
    element = """Jobs  <br>
    <table><thead><tr><th>Actor name</th><th>Service Name</th><th>Action name</th></tr></thead>
    """
    for job in jobs:
        element += "<tr>"
        element += "<td>" + job['actor_name'] + "</td>"
        element += "<td>" + job['actor_name'] + "</td>"
        element += "<td>" + job['actor_name'] + "</td>"
        element += "</tr>"
    element += "</table>"
    args.doc.applyTemplate({'element': element})

    params.result = (args.doc, args.doc)
    return params

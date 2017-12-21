from urllib import parse

def main(j, args, params, tags, tasklet):
    page = args.page

    from subprocess import PIPE, Popen
    jobid = args.getTag('jobid')
    if not j.core.jobcontroller.db.jobs.exists(jobid):
        page.addMessage("Job with id %s was not found" % jobid)
        params.result = page
        return params

    job = j.core.jobcontroller.db.jobs.get(jobid)
    stats = j.sal.fs.getTempFileName()

    job = job.objectGet()
    j.sal.fs.writeFile(filename=stats, contents=job.model.dbobj.profileData, append=False)

    host = args.requestContext.env.get('HTTP_HOST', 'localhost')
    if host.find(":") != -1:
        host = host.split(":")[0]

    p = Popen(['timeout', '1s', 'python3', '-u', '/usr/local/bin/snakeviz','-H', '0.0.0.0', '-s', stats], stdout=PIPE)

    line = p.stdout.readline().decode()
    while 'http' not in line:
        line = p.stdout.readline()
        line = line.decode()

    u = parse.urlparse(line)
    u2 = u._replace(netloc="%s:%s" % (host, u.port))
    page.addHTML("<iframe src=%s frameborder='0' width=100%% height=600 position=absolute></iframe>" % u2.geturl())

    params.result = page

    return params

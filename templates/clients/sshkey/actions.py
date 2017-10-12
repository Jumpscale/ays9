from js9 import j
def input(job):
    """
    create key, if it doesn't exist
    """

    # THIS ONE IS FIXED
    args = job.model.args

    if 'key.path' in job.model.args and job.model.args['key.path'] is not None and job.model.args['key.path'] != '':
        path = job.model.args['key.path']
        if not j.sal.fs.exists(path, followlinks=True):
            raise j.exceptions.Input(message="Cannot find ssh key:%s for service:%s" %
                                     (path, job.service), level=1, source="", tags="", msgpub="")

        args['key.path'] = j.sal.fs.joinPaths(job.service.path, "id_rsa")
        j.sal.fs.createDir(job.service.path)
        j.sal.fs.copyFile(path, args['key.path'])
        j.sal.fs.copyFile(path + '.pub', args['key.path'] + '.pub')
        args["key.priv"] = j.sal.fs.fileGetContents(path)
        args["key.pub"] = j.sal.fs.fileGetContents(path + '.pub')

    if 'key.name' in job.model.args and bool(job.model.args.get('key.name')):
        path = j.clients.ssh.SSHKeyGetPathFromAgent(job.model.args['key.name'])
        if not path or not j.sal.fs.exists(path, followlinks=True):
            raise j.exceptions.Input(message="Cannot find ssh key:%s for service:%s" %
                                     (path, job.service), level=1, source="", tags="", msgpub="")

        args["key.priv"] = j.sal.fs.fileGetContents(path)
        args["key.pub"] = j.sal.fs.fileGetContents(path + '.pub')
        args["key.name"] = job.model.args["key.name"]
        args["key.path"] = j.sal.fs.joinPaths(job.service.path, job.model.args['key.name'])
        j.sal.fs.createDir(job.service.path)
        j.sal.fs.copyFile(path, j.sal.fs.joinPaths(job.service.path, args["key.path"]))
        j.sal.fs.copyFile(path + '.pub', j.sal.fs.joinPaths(job.service.path, '%s.%s' % (args["key.path"], 'pub')))

    if 'key.priv' not in args or args['key.priv'].strip() == "":
        print("lets generate private key")
        args['key.path'] = j.sal.fs.joinPaths(job.service.path, "id_rsa")
        j.sal.fs.createDir(job.service.path)
        j.sal.fs.remove(args['key.path'])
        cmd = "ssh-keygen -q -t rsa -f %s -N ''" % (args['key.path'])
        rc, out, err = j.sal.process.execute(cmd, die=True, outputStderr=False)
        args["key.priv"] = j.sal.fs.fileGetContents(args['key.path'])
        args["key.pub"] = j.sal.fs.fileGetContents(args['key.path'] + '.pub')

    j.sal.fs.chmod(args['key.path'], 0o600)
    j.sal.fs.chmod(args['key.path']+ '.pub', 0o600)

    return args

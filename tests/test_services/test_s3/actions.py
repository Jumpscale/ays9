def init_actions_(service, args):
    """
    this needs to returns an array of actions representing the depencies between actions.
    Looks at ACTION_DEPS in this module for an example of what is expected
    """
    return {
        'test': ['install']
    }


def test(job):
    import sys
    import time
    try:
        log = j.logger.get('test')
        log.addHandler(j.logger._LoggerFactory__fileRotateHandler('tests'))
        log.info('Test started')
        service = job.service
        repo = service.aysrepo
        scality = repo.servicesFind(actor='scality', name='app')[0]
        keyaccess = scality.model.data.keyAccess
        keysecret = scality.model.data.keySecret
        s3 = repo.servicesFind(actor='s3')[0]
        fqdn = s3.model.data.fqdn
        s3vm = repo.servicesFind(actor='os.ssh.ubuntu', name='s3vm')[0]
        s3vm_exe = s3vm.executor.get_prefab()

        log.info('Install s3cmd on the s3_vm and connecting it to s3 server')
        s3vm_exe.core.run('echo "Y" | apt-get install s3cmd')
        s3vm_exe.core.run('echo "127.0.0.1 %s" >> /etc/hosts' % fqdn)
        config = """
        [default]
        access_key = {0}
        secret_key = {1}
        host_base = {2}
        host_bucket = {2}
        signature_v2 = True
        use_https = False
        """.format(keyaccess, keysecret, fqdn)
        s3vm_exe.core.run("cd /root; echo '{}' > .s3cfg".format(config))

        log.info('Creating bucket')
        time.sleep(60)
        t1 = time.time()
        while(True):
            now = time.time()
            time.sleep(5)
            try:
                res = s3vm_exe.core.run("s3cmd ls")
            except:
                continue
            if res[1] == '' or now > t1 + 300:
                break
        bucket = s3vm_exe.core.run("s3cmd mb s3://test")
        if bucket[1] != "Bucket 's3://test/' created":
            service.model.data.result = 'FAILED : {} {}'.format('test_s3', str(sys.exc_info()[:2]))
            service.save()
            return

        log.info('Put file into bucket')
        s3vm_exe.core.run('cd /root; touch test_file')
        s3vm_exe.core.run('cd /root; s3cmd put test_file s3://test/check')

        log.info('Get File from bucket')
        s3vm_exe.core.run('s3cmd get s3://test/check')
        check = s3vm_exe.core.run('ls check |  wc -l')
        if check[1] != '1':
            service.model.data.result = 'FAILED : {} {}'.format('test_s3', str(sys.exc_info()[:2]))
            service.save()
            return

        service.model.data.result = 'OK : {} '.format('test_s3')
        log.info('Test Ended')

    except:
        service.model.data.result = 'ERROR : {} {}'.format('test_s3', str(sys.exc_info()[:2]))
    log.info('Test Ended')
    service.save()

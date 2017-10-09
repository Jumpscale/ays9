def init_actions_(service, args):
    """
    this needs to returns an array of actions representing the depencies between actions.
    Looks at ACTION_DEPS in this module for an example of what is expected
    """
    return {
        'test': ['install']
    }


def test(job):
    import requests
    import os
    import sys
    import time
    import zipfile
    from io import BytesIO
    try:
        os.system('apt-get update')
        os.system('apt-get install python3-xlrd')
        from xlrd import open_workbook
        os.mkdir('{}/resource_mang'.format(os.getcwd()))
        cwd = os.getcwd() + '/resource_mang'
        os.mkdir('{}/resourcetracking'.format(cwd))
        log = j.logger.get('test')
        log.addHandler(j.logger._LoggerFactory__fileRotateHandler('tests'))
        log.info('Test started')
        service = job.service

        log.info('Getting authentication session')
        g8client = service.producers['g8client'][0]
        username = g8client.model.data.login
        password = g8client.model.data.password
        url = 'https://' + g8client.model.data.url
        login_url = url + '/restmachine/system/usermanager/authenticate'
        credential = {'name': username, 'secret': password}
        session = requests.Session()
        session.post(url=login_url, data=credential)

        log.info('triggering jumscript on the controller to collect account\'s information')
        js_url = url + '/restmachine/system/agentcontroller/executeJumpscript'
        cont_params = {'organization': 'jumpscale' ,'name': 'resmonitoring',
                    'gid': 27, 'role': 'controller'}
        response = session.post(url=js_url, data=cont_params)
        if response.status_code != 200:
            service.model.data.result = 'FAILED : {} {} {}'.format('test_account_resources',
                                        'response status is not equal 200',str(sys.exc_info()[:2]))
            os.system('rm -rf {}'.format(cwd))
            service.save()
            return

        log.info('triggering jumscript on the master to collect account\'s information')
        time.sleep(3)
        master_params = {'organization': 'greenitglobe' ,'name': 'aggregate_account_data',
                        'gid': 27, 'role': 'master'}
        response = session.post(url=js_url, data=master_params)
        if response.status_code != 200:
            service.model.data.result = 'FAILED : {} {} {}'.format('test_account_resources',
                                        'response status is not equal 200',str(sys.exc_info()[:2]))
            os.system('rm -rf {}'.format(cwd))
            service.save()
            return

        log.info('Getting the account information binary file')
        ovc_client = j.clients.openvcloud.getFromService(g8client)
        account  = g8client.model.data.account
        accountId = ovc_client.account_get(account).id
        end = time.time()
        start = end - 60*60
        api_url = url + '/restmachine/cloudapi/accounts/getConsumption?accountId={}&start={}&end={}'.format(accountId, start, end)
        response = session.get(url=api_url)
        if response.status_code != 200:
            service.model.data.result = 'FAILED : {} {} {}'.format('test_account_resources',
                                        'response status is not equal 200',str(sys.exc_info()[:2]))
            os.system('rm -rf {}'.format(cwd))
            service.save()
            return
        if response.text == '':
            service.model.data.result = 'FAILED : {} {} {}'.format('test_account_resources',
                                        'response text is empty, it should contains binary info',
                                        str(sys.exc_info()[:2]))
            os.system('rm -rf {}'.format(cwd))
            service.save()
            return

        log.info('Writing capnp schema into a file')
        first_part = '        @0x934efea7f327fff0;'
        second_part = """
        struct CloudSpace {
          cloudSpaceId @0 :Int32;
          accountId @1 :Int32;
          machines @2 :List(VMachine);
          state @3 :Text;
          struct VMachine {
            id @0 :Int32;
            type @1 :Text;
            vcpus @2 :Int8;
            cpuMinutes @3 :Float32;
            mem @4 :Float32;
            networks @5 :List(Nic);
            disks @6 :List(Disk);
            imageName @7 :Text;
            status @8 :Text;
            struct Nic {
              id @0 :Int32;
              type @1 :Text;
              tx @2 :Float32;
              rx @3 :Float32;
            }
            struct Disk {
                id @0 :Int32;
                size @1 :Float32;
                iopsRead  @2 :Float32;
                iopsWrite  @3 :Float32;
                iopsReadMax @4 :Float32;
                iopsWriteMax @5 :Float32;
            }
          }
        }

        struct Account {
          accountId @0  :UInt32;
          cloudspaces @1 :List(CloudSpace);
        }
        """

        res_mon_schema = first_part + second_part
        os.system("touch {}/resourcemonitoring.capnp".format(cwd))
        with open('{}/resourcemonitoring.capnp'.format(cwd), 'w') as f:
            f.write('{}'.format(res_mon_schema))

        log.info('Running python script to convert binary file to xls file')
        bin_to_xls_script = """
        from JumpScale import j
        import argparse
        import os
        import xlwt
        import pprint
        import capnp
        from datetime import datetime
        from os import listdir

        #now = datetime.utcnow()
        capnp.remove_import_hook()
        schemapath = os.path.join('{0}', 'resourcemonitoring.capnp')
        resources_capnp = capnp.load(schemapath)
        root_path = '{0}/resourcetracking'
        accounts = listdir(root_path)

        book = xlwt.Workbook(encoding='utf-8')
        nosheets = True
        for dirpath, subdirs, files in os.walk(root_path):
            for x in files:
                file_path = os.path.join(dirpath, x)

        for account in accounts:
            nosheets = False
            sheet = book.add_sheet('account %s' % account)
            sheet.write(0, 0, 'Cloud Space ID')
            sheet.write(0, 1, 'Machine Count')
            sheet.write(0, 2, 'Total Memory')
            sheet.write(0, 3, 'Total VCPUs')
            sheet.write(0, 4, 'Disk Size')
            sheet.write(0, 5, 'Disk IOPS Read')
            sheet.write(0, 6, 'Disk IOPS Write')
            sheet.write(0, 7, 'NICs TX')
            sheet.write(0, 8, 'NICs RX')

            with open(file_path, 'rb') as f:
                account_obj = resources_capnp.Account.read(f)
                for idx, cs in enumerate(account_obj.cloudspaces):
                    cs_id = cs.cloudSpaceId
                    machines = len(cs.machines)
                    vcpus = 0
                    mem = 0
                    disksize = 0
                    disk_iops_read = 0
                    disk_iops_write = 0
                    nics_tx = 0
                    nics_rx = 0
                    for machine in cs.machines:
                        vcpus += machine.vcpus
                        mem += machine.mem
                        for disk in machine.disks:
                            disk_iops_read += disk.iopsRead
                            disk_iops_write += disk.iopsWrite
                            disksize += disk.size
                        for nic in machine.networks:
                            nics_tx += nic.tx
                            nics_rx += nic.rx
                    sheet.write(idx + 1, 0, cs_id)
                    sheet.write(idx + 1, 1, machines)
                    sheet.write(idx + 1, 2, mem)
                    sheet.write(idx + 1, 3, vcpus)
                    sheet.write(idx + 1, 4, disksize)
                    sheet.write(idx + 1, 5, disk_iops_read)
                    sheet.write(idx + 1, 6, disk_iops_write)
                    sheet.write(idx + 1, 7, nics_tx)
                    sheet.write(idx + 1, 8, nics_rx)

        if nosheets is False:
            book.save('example.xls')
        else:
            print('No data found')
        """.format(cwd)

        os.system("touch {}/export_acc.py".format(cwd))
        with open('{}/export_acc.py'.format(cwd), 'w') as f:
            f.write('{}'.format(bin_to_xls_script))
        os.system("sed -i 's/        //' {}/export_acc.py".format(cwd))
        os.system("sed -i 's/        //' {}/resourcemonitoring.capnp".format(cwd))

        log.info('Extracting .xls zip file')
        file = zipfile.ZipFile(BytesIO(response.content))
        file.extractall('{}/resourcetracking'.format(cwd))
        os.system('jspython {}/export_acc.py'.format(cwd))
        os.system('mv example.xls {}'.format(cwd))
        # Extract info from xls file
        vdc1 = g8client.consumers['vdc'][0]
        vdc2 = g8client.consumers['vdc'][1]
        vdc1_id = vdc1.model.data.cloudspaceID
        vdc2_id = vdc2.model.data.cloudspaceID
        css_ids = [vdc1_id, vdc2_id]

        vms_vdc1_count = len(vdc1.consumers['node'])
        vms_vdc2_count = len(vdc2.consumers['node'])
        vms_cs_count = [vms_vdc1_count, vms_vdc2_count]

        rand_vm = vdc1.consumers['node'][0]
        used_size = rand_vm.model.data.sizeID
        bdisk_size = rand_vm.model.data.bootdiskSize
        # This should include all of the sizes
        sizes = ovc_client.api.cloudapi.sizes.list(cloudspaceId=vdc1.model.data.cloudspaceID)
        size = [i for i in sizes1 if i['id']==used_size][0]
        total_mem_cs = [vms_vdc1_count*size['memory'], vms_vdc2_count*size['memory']]
        total_cpu_cs = [vms_vdc1_count*size['vcpus'], vms_vdc2_count*size['vcpus']]
        total_diskz_cs = [vms_vdc1_count*bdisk_size, vms_vdc2_count*bdisk_size]

        log.info('Extracting info from xls file')
        wb = open_workbook("{}/example.xls".format(cwd))
        wb.sheet_by_index(0)
        s = wb.sheet_by_index(0)
        cs1_id = int(s.cell(1, 0).value)
        cs1_vms_nums = int(s.cell(1, 1).value)
        cs1_total_mem = int(s.cell(1, 2).value)
        cs1_total_vcpu = int(s.cell(1, 3).value)
        cs1_Disk_size = int(s.cell(1, 4).value)

        cs2_id = int(s.cell(2, 0).value)
        cs2_vms_nums = int(s.cell(2, 1).value)
        cs2_total_mem = int(s.cell(2, 2).value)
        cs2_total_vcpu = int(s.cell(2, 3).value)
        cs2_Disk_size = int(s.cell(2, 4).value)

        if cs1_id == vdc1_id:
            c1 = 0; c2 = 1
        else:
            c1 = 1; c2 = 0

        log.info('Validating if the account info in the .xls file is correct')
        if cs1_id != css_ids[c1]:
            service.model.data.result = 'FAILED : {} {} {}'.format('test_account_resources',
                                        'cloudspace1_id is wrong',str(sys.exc_info()[:2]))
            os.system('rm -rf {}'.format(cwd))
            service.save()
            return

        if cs2_id != css_ids[c2]:
            service.model.data.result = 'FAILED : {} {} {}'.format('test_account_resources',
                                        'cloudspace2_id is wrong',str(sys.exc_info()[:2]))
            os.system('rm -rf {}'.format(cwd))
            service.save()
            return

        if cs1_vms_nums != vms_cs_count[c1]:
            service.model.data.result = 'FAILED : {} {} {}'.format('test_account_resources',
                                        'cloudspace1\'s vms count is wrong', str(sys.exc_info()[:2]))
            os.system('rm -rf {}'.format(cwd))
            service.save()
            return

        if cs2_vms_nums != vms_cs_count[c2]:
            service.model.data.result = 'FAILED : {} {} {}'.format('test_account_resources',
                                        'cloudspace2\'s vms count is wrong', str(sys.exc_info()[:2]))
            os.system('rm -rf {}'.format(cwd))
            service.save()
            return

        if cs1_total_mem != total_mem_cs[c1]:
            service.model.data.result = 'FAILED : {} {} {}'.format('test_account_resources',
                                        'cloudspace1\'s total memory is wrong', str(sys.exc_info()[:2]))
            os.system('rm -rf {}'.format(cwd))
            service.save()
            return

        if cs2_total_mem != total_mem_cs[c2]:
            service.model.data.result = 'FAILED : {} {} {}'.format('test_account_resources',
                                        "cloudspace2\'s total memory is wrong", str(sys.exc_info()[:2]))
            os.system('rm -rf {}'.format(cwd))
            service.save()
            return

        if cs1_total_vcpu != total_cpu_cs[c1]:
            service.model.data.result = 'FAILED : {} {} {}'.format('test_account_resources',
                                        "cloudspace1\'s total Vcpus is wrong", str(sys.exc_info()[:2]))
            os.system('rm -rf {}'.format(cwd))
            service.save()
            return

        if cs2_total_vcpu != total_cpu_cs[c2]:
            service.model.data.result = 'FAILED : {} {} {}'.format('test_account_resources',
                                        "cloudspace2\'s total Vcpus is wrong", str(sys.exc_info()[:2]))
            os.system('rm -rf {}'.format(cwd))
            service.save()
            return

        if cs1_Disk_size != total_diskz_cs[c1]:
            service.model.data.result = 'FAILED : {} {} {}'.format('test_account_resources',
                                        "cloudspace1\'s total Bootdisk sizes is wrong", str(sys.exc_info()[:2]))
            os.system('rm -rf {}'.format(cwd))
            service.save()
            return

        if cs2_Disk_size != total_diskz_cs[c2]:
            service.model.data.result = 'FAILED : {} {} {}'.format('test_account_resources',
                                        "cloudspace2\'s total Bootdisk sizes is wrong", str(sys.exc_info()[:2]))
            os.system('rm -rf {}'.format(cwd))
            service.save()
            return
        os.system('rm -rf {}'.format(cwd))
        service.model.data.result = 'OK : {} '.format('test_owncloud_install')
    except:
        service.model.data.result = 'ERROR : {} {}'.format('test_account_resources', str(sys.exc_info()[:2]))
        os.system('rm -rf {}'.format(cwd))
    log.info('Test Ended')
    service.save()

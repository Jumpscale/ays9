"""
Test runner module for AYS9

How to use it:
from ays_testrunner.testrunner import AYSCoreTestRunner
backend_config = {'URL': 'du-conv-2.demo.greenitglobe.com', 'IYO_APPID': '***', 'IYO_SECRET': '****', 'ACCOUNT': 'aystestrunner', 'LOCATION': 'du-conv-2'}
core = AYSCoreTestRunner('core', config={'bp_paths': ['/opt/code/github/jumpscale/ays9/tests/bp_test_templates/core/test_auto_behavior.yaml', "/tmp/grouptest"], 'BACKEND_ENV': backend_config,
'TEST_TIMEOUT': 300})
core.run()
"""
from js9 import j

import os
import random
from redis import Redis
from rq import Queue
import time
import logging
import requests

AYS_CORE_BP_TESTS_PATH = [j.sal.fs.joinPaths(j.sal.fs.getParent(j.sal.fs.getParent(__file__)), 'tests', 'bp_test_templates', 'core')]

AYS_NON_CORE_BP_TESTS_PATH = []

AYS_TESTRUNNER_REPO_NAME = 'ays_testrunner'
AYS_TESTRUNNER_REPO_GIT = 'https://github.com/ahussein/ays_testrunner.git'
DEFAULT_TEST_TIMEOUT = 600 # 10 min timeout per test
DEFAULT_IYO_BASEURL = "https://itsyou.online/api"
DEFAULT_OVC_PORT = 443
DEFAULT_ACCOUNT_NAME = 'aystestrunner'
DEFAULT_AYS_CONFIGURE_JS_LOCATION_ENDPOINT = 'http://localhost:5000/ays/repository/{repo_name}/configure-jslocation'


def configure_backend_clients(repo_info, config, logger=None):
    """
    Configures IYO and OVC clients that will be used during running the tests

    @param repo_info: repository information
    @param config: backend configurations
    @param logger: logger object to use for logging
    """
    errors = []
    if logger is None:
        logger = j.logger.logging

    required_configs = ['URL', 'IYO_APPID', 'IYO_SECRET']
    missing_configs = []
    for item in required_configs:
        if item not in config:
            missing_configs.append(item)
    if missing_configs:
        raise ValueError('The following configurations are missing while configuring backend clients: {}'.format(missing_configs))
    
    instance_name = 'aystestrunner'
    instance_to_check = '{}_{}'.format(repo_info['name'], instance_name)
    # configuring IYO client
    if instance_to_check in j.clients.itsyouonline.list():
        iyo_client = j.clients.itsyouonline.get(instance=instance_to_check)
    else:
        logger.info('Configuring IYO client for repo {}'.format(repo_info['name']))
        data = {
                "instance": instance_name, 
                "jslocation": "j.clients.itsyouonline",
                "data" :{
                    "application_id_": config['IYO_APPID'],
                    "secret_": config['IYO_SECRET'],
                    "baseurl": DEFAULT_IYO_BASEURL
                }
        }
        url = DEFAULT_AYS_CONFIGURE_JS_LOCATION_ENDPOINT.format(repo_name=repo_info['name'])
        res = requests.post(url, json=data)
        if res.status_code != 201:
            errors.append('Failed to configure IYO client for repo {}'.format(repo_info['name']))
        else:
            iyo_client = j.clients.itsyouonline.get(instance=instance_to_check)
        
    # configure OVC client
    if instance_to_check in j.clients.openvcloud.list():
        ovc_client = j.clients.openvcloud.get(instance=instance_to_check)
    else:
        logger.info('Configuring OVC client for repo {}'.format(repo_info['name']))
        data = {
                "instance": instance_name,
                "jslocation": "j.clients.openvcloud",
                "data" : {
                    "address": config['URL'],
                    "port": DEFAULT_OVC_PORT
            }
        }
        res = requests.post(url, json=data)
        if res.status_code != 201:
            errors.append('Failed to configure OVC client for repo {}'.format(repo_info['name']))
        else:
            ovc_client = j.clients.openvcloud.get(instance=instance_to_check)

    if errors:
        raise RuntimeError('Errors while configuring clients for repo {}'.format(repo_info['name']))
    return iyo_client, ovc_client



def check_status_code(res, expected_status_code=200, logger=None):
    """
    Check if a response object has the expected status code

    returns (response object, True/False)
    """
    if logger is None:
        logger = j.logger.logging

    logger.debug('Validating response status code {} with expected status code {}'.format(res.status_code, expected_status_code))
    if res.status_code == expected_status_code:
        return res, True
    return res, False

def ensure_test_repo(cli, repo_name, logger=None, config=None):
    """
    Ensure a new repo for running tests is created with unique name
    This will also make sure to create a new instance of the IYO and OVC client configurations for this repo

    """

    if logger is None:
        logger = j.logger.logging
    
    if config is None:
        config = {}

    logger.debug('Ensuring test repo with name {}'.format(repo_name))
    result = None
    name_exist = False
    res, ok = check_status_code(cli.listRepositories())
    if ok:
        for repo_info in res.json():
            if repo_info['name'] == repo_name:
                name_exist = True

                break
        if name_exist:
            logger.debug('Repo name {} already exists'.format(repo_name))
            # generate new rpeo name
            suffix = random.randint(1, 10000)
            repo_name = '%s%s' % (repo_name, suffix)
            result = ensure_test_repo(cli, repo_name, config=config)
        else:
            # create repo with that name
            res, ok = check_status_code(cli.createRepository(data={'name': repo_name, 'git_url': AYS_TESTRUNNER_REPO_GIT}), 201)
            if ok is True:
                result = res.json()
        configure_backend_clients(repo_info=result, config=config.get('BACKEND_ENV', {}), logger=logger)
    else:
        logger.info('Failed to list Repositories. Error: {}'.format(res.text))

    return result

def execute_blueprint(cli, blueprint, repo_info, logger=None):
    """
    Execute a blueprint
    """

    if logger is None:
        logger = j.logger.logging

    errors = []
    logger.info('Executing blueprint [{}]'.format(blueprint))
    try:
        res, ok = check_status_code(cli.executeBlueprint(data={}, blueprint=blueprint, repository=repo_info['name']))
        if not ok:
            msg = 'Failed to execute blueprint {} in repository {}. Error: {}'.format(blueprint, repo_info['name'], res.text)
            logger.error(msg)
            errors.append(msg)
    except Exception as ex:
        msg = 'Failed to execute blueprint {} in repository {}. Error: {}'.format(blueprint, repo_info['name'], ex)
        logger.error(msg)
        errors.append(msg)
    return errors

def create_run(cli, repo_info, logger=None):
    """
    Create a run and execute it
    """

    if logger is None:
        logger = j.logger.logging

    errors = []
    logger.info('Creating a new run')
    curdir = j.sal.fs.getcwd()
    j.sal.fs.changeDir(repo_info['path'])
    cmd = 'ays run create -y --force -f'
    try:
        j.tools.prefab.local.core.run(cmd, timeout=0)
    except Exception as e:
        errors.append('Failed to create run. Error: {}'.format(e))
    finally:
        j.sal.fs.changeDir(curdir)

    return errors

def report_run(cli, repo_info, logger=None):
    """
    Check the created run and services for errors and report them if found
    check run status and report errors and logs if status is not ok
    if run status is ok then check the services result attribute and report errors if found
    """

    if logger is None:
        logger = j.logger.logging

    errors = []
    # check the run itself if there were errors while executing it
    res, ok = check_status_code(cli.listRuns(repository=repo_info['name']))
    if ok:
        runs_info = res.json()
        for run_info in runs_info:
            runid = run_info['key']
            if run_info['state'] == 'error':
                # get run
                res, ok = check_status_code(cli.getRun(runid, repo_info['name']))
                if ok:
                    run_details = res.json()
                    # run has steps and each step consists of jobs
                    for step in run_details['steps']:
                        if step['state'] == 'error':
                            for job in step['jobs']:
                                msg = 'Actor: [{}] Action: [{}]'.format(job['actor_name'], job['action_name'])
                                errors.append(msg)
                                errors.append('-' * len(msg))
                                for log in job['logs']:
                                    if log['log']:
                                        errors.append(log['log'])

                else:
                    errors.append('Failed to retieve run [{}]'.format(runid))

        # after checking the runs, we need to check the services
        res, ok = check_status_code(cli.listServices(repo_info['name']))
        if ok:
            services = res.json()
            for service_info in services:
                res, ok = check_status_code(cli.getServiceByName(service_info['name'], service_info['role'], repo_info['name']))
                if ok:
                    service_details = res.json()
                    if service_details['data'].get('result') and not service_details['data']['result'].startswith('OK'):
                        msg = 'Service role: [{}] Service instance: [{}]'.format(service_info['role'], service_info['name'])
                        errors.append(msg)
                        errors.append('-' * len(msg))
                        errors.append(service_details['data']['result'])
                else:
                    errors.append('Failed to get service [{}!{}]'.format(service_info['role'], service_info['name']))
        else:
            errors.append('Failed to list services')
    else:
        errors.append('Failed to list runs')

    return errors

def collect_tests(paths, logger=None, setup=None, teardown=None, repo_info=None, config=None):
    """
    Collects all test bp from the given paths
    This will only scan only one level of the paths and collect all the files that that ends with .yaml and .bp files
    If path in the list is a file then it will be considered a test file
    For all the directories on the same level, a group test will be created for each directory
    """

    if logger is None:
        logger = j.logger.logging

    result = []
    logger.info('Collecting tests from paths {}'.format(paths))
    for path in paths:
        if not j.sal.fs.exists(path):
            logger.error('Path {} does not exist'.format(path))
            continue
        if j.sal.fs.isFile(path):
            name = j.sal.fs.getBaseName(path)
            result.append(AYSTest(name=name, path=path, setup=setup, teardown=teardown, repo_info=repo_info, config=config))
            continue
        for dir_ in j.sal.fs.listDirsInDir(path):
            logger.debug('Creating group test for path {}'.format(dir_))
            result.append(AYSGroupTest(name=j.sal.fs.getBaseName(dir_), path=dir_, config=config))
        for file_ in sorted([file__ for file__ in j.sal.fs.listFilesInDir(path) if not j.sal.fs.getBaseName(file__).startswith('_') and
                                                                                  (file__.endswith('{}yaml'.format(os.path.extsep)) or
                                                                                  file__.endswith('{}bp'.format(os.path.extsep)))]):
            logger.debug('Creating test for path {}'.format(file_))
            result.append(AYSTest(name=j.sal.fs.getBaseName(file_), path=file_, setup=setup, teardown=teardown, repo_info=repo_info, config=config))
    return result


class AYSGroupTest:
    """
    Represet a group of test bps that depend on each other
    These tests will be executed in order(based on the file name)
    """
    def __init__(self, name, path, logger=None, config=None):
        """
        Initialize group test

        @param name: Name of the group
        @param path: Path to the hosting folder of the test bps
        @param logger: Logger object to use for logging
        @param config: extra configurations dictionary
        """
        self._name = name
        self._path = path
        self._errors = []
        self._config = config if config is not None else {}
        if logger is None:
            # FIXME: problem with using the js logger when pickling the object
            # self._logger = j.logger.get('aystestrunner.AYSTest.{}'.format(name))
            self._logger = logging.getLogger()
        else:
            self._logger = logger
        # create a repo per group test
        try:
            self._cli = j.clients.atyourservice.get().api.ays
            self._repo_info = ensure_test_repo(self._cli, AYS_TESTRUNNER_REPO_NAME, logger=self._logger, config=config)
        except Exception as ex:
            self._repo_info = None
            self._errors.append('Failed to create new ays repository for test {}'.format(self._name))
            
        self._tests = collect_tests(paths=[path], logger=self._logger, setup=self.setup, teardown=self.singletest_teardwon, repo_info=self._repo_info, config=config)


    @property
    def name(self):
        return self._name

    @property
    def duration(self):
        """
        Returns the duration of the test. If any of the member tests are still running or not started yet then return -1
        """
        result = -1
        for test in self._tests:
            if test.duration == -1:
                result = -1
                break
            else:
                result += test.duration
        return result
    

    @property
    def errors(self):
        return self._errors


    def setup(self):
        """
        Setup steps
        """
        pass


    def singletest_teardwon(self):
        """
        Override single test member teardown
        """
        pass


    def teardown(self):
        """
        Teardown steps
        """
        repo_exist = False
        try:
            for test in self._tests:
                test.teardown()
            res, ok = check_status_code(self._cli.listRepositories())
            if ok:
                for repo_info in res.json():
                    if repo_info['name'] == self._repo_info.get('name', None):
                        repo_exist = True
                        break

            if repo_exist:
                # destroy repo
                self._cli.destroyRepository(data={}, repository=self._repo_info['name'])
                # delete repo
                self._cli.deleteRepository(repository=self._repo_info['name'])
        except Exception as err:
            self._errors.append('Errors while executing teardown for group test {}. Errors: {}'.format(self._name, err))


    def replace_placehlders(self, config):
        """
        Use a given configuration to replace the content of the bp after replacing all the placeholder with values
        from the configuration
        """
        for test in self._tests:
            test.replace_placehlders(config=config)


    def run(self):
        """
        Run Tests in the group
        """
        self._logger.info("Running gourp tests {}".format(self._name))
        self.setup()
        for test in self._tests:
            test.run()
            if test.errors:
                self._errors = test.errors
                break

        # only teardown if there is no errors, otherwise leave repo test for inspection 
        if not self._errors:
            self.teardown()
            
        return self._errors



class AYSTest:
    """
    Represents an AYS test bp
    """
    def __init__(self, name, path, logger=None, setup=None, teardown=None, repo_info=None, config=None):
        """
        Initialize the test

        @param name: Name of the test
        @param path: Path to the test bp
        @param logger: Logger object to use for logging
        @param setup: Setup function to be called before the test
        @param teardown: Teardown function to be called after the test
        @param config: Extra configurations dictionary
        """
        self._path = path
        self._name = name
        self._repo_info = {}
        self._errors = []
        self._cli = None
        self._starttime = None
        self._endtime = None
        self._config = config if config is not None else {}
        if setup is not None:
            self.setup = setup
        if teardown is not None:
            self.teardown = teardown

        if logger is None:
            # FIXME: problem with using the js logger when pickling the object
            # self._logger = j.logger.get('aystestrunner.AYSTest.{}'.format(name))
            self._logger = logging.getLogger()
        else:
            self._logger = logger

        # create a repo per test
        try:
            self._cli = j.clients.atyourservice.get().api.ays
            if repo_info is None:
                self._repo_info = ensure_test_repo(self._cli, AYS_TESTRUNNER_REPO_NAME, logger=self._logger, config=config)
            else:
                self._repo_info = repo_info
        except Exception as ex:
            self._errors.append('Failed to create new ays repository for test {}'.format(self._name))

    @property
    def starttime(self):
        return self._starttime

    @starttime.setter
    def starttime(self, value):
        self._starttime = value

    @property
    def endtime(self):
        return self._endtime

    @starttime.setter
    def endtime(self, value):
        self._endtime = value

    @property
    def duration(self):
        if self._starttime and self._endtime:
            return self._endtime - self._starttime
        else:
            return -1


    def replace_placehlders(self, config):
        """
        Use a given configuration to replace the content of the bp after replacing all the placeholder with values
        from the configuration
        """
        sed_base_command = 'sed s/\<{key}\>/{value}/g {path} > {path}.processed'
        self._logger.info('Replacing placeholders for test blueprint {}'.format(self._path))
        for item, value in config.items():
            cmd = sed_base_command.format(key=item, value=value, path=self._path)
            try:
                j.tools.prefab.local.core.run(cmd, showout=False)
            except:
                self._logger.warning('Failed to replace placeholder {}'.format(item))

    def setup(self):
        """
        Execute any setup setps
        """
        pass


    def teardown(self):
        """
        Execute any teardown steps
        """
        repo_exist = False
        try:
            res, ok = check_status_code(self._cli.listRepositories())
            if ok:
                for repo_info in res.json():
                    if repo_info['name'] == self._repo_info.get('name', None):
                        repo_exist = True
                        break

            if repo_exist:
                # destroy repo
                self._cli.destroyRepository(data={}, repository=self._repo_info['name'])
                # delete repo
                self._cli.deleteRepository(repository=self._repo_info['name'])
        except Exception as err:
            self._errors.append('Failed to destroy/delete repository {}. Error: {}'.format(self._repo_info['name'], err))


    def run(self):
        """
        Run test by executing the following steps
        - Create a repo
        - Copy the blueprint to the repo
        - Execute the blueprint
        - Create a run and execute it
        - Collect run results
        - Destroy repo
        """
        if not self._errors:
            self.setup() 
            try:
                if self._repo_info is None:
                    self._errors.append('Failed to create new ays repository for test {}'.format(self._name))
                else:
                    j.sal.fs.moveFile('{}.processed'.format(self._path), os.path.join(self._repo_info['path'], 'blueprints', self._name))
                    # execute bp
                    self._errors.extend(execute_blueprint(self._cli, self._name, self._repo_info, logger=self._logger))
                    if not self._errors:
                        # create run and execute it
                        self._errors.extend(create_run(self._cli, self._repo_info, logger=self._logger))
                        # report run
                        self._errors.extend(report_run(self._cli, self._repo_info, logger=self._logger))
            except Exception as err:
                self._errors.append('Test {} failed with error: {}'.format(self._name, err))

            # only teardown if there is no errors, otherwise leave repo test for inspection 
            if not self._errors:
                self.teardown()

        return self._errors


    @property
    def name(self):
        return self._name

    @property
    def errors(self):
        return self._errors

    @errors.setter
    def errors(self, errors):
        self._errors = errors

    @property
    def repo_info(self):
        return self._repo_info


class BaseRunner:
    """
    Base class for test runners
    """
    def __init__(self, name, config=None):
        """
        Intialize test runner
        """
    
        if config is None:
            config = {}
        self._config = config
        self._logger = j.logger.get('aystestrunner.{}'.format(name))
        self._name = name
        self._failed_tests = {}
        self._tests = []
        self._default_bp_paths = []
        self._ovc_client = None


    def _pre_process_tests(self):
        """
        Execute any required pre-processing steps
        """
        for test in self._tests:
            test.replace_placehlders(self._config.get('BACKEND_ENV', {}))


    def run(self):
        """
        Run tests and report their results
        collects tests
        pre-process tests
        execute setup steps
        execute test
        execute teardown setps
        report tests
        """
        try:
            jobs = {}
            self._tests = collect_tests(paths=self._config.get('bp_paths', self._default_bp_paths), logger=self._logger, config=self._config)
            self._pre_process_tests()
            for test in self._tests:
                self._logger.info('Running test {}'.format(test.name))
                try:
                    test.starttime = time.time()
                    test.run()
                    test.endtime = time.time()
                except Exception as e:
                    test.errors.append('Failed to run test {}. Errors: [{}]'.format(test.name, str(e)))

                if test.errors:
                    self._failed_tests[test] = test
            # report final results
            self._report_results()
        finally:
            # clean up the BACKEND env if requested
            if self._config.get('BACKEND_ENV_CLEANUP', False):
                self._cleanup()


    def _cleanup(self):
        """
        Will clean up a BACKEND environment. Typically should be called for test environment where all the resources created can be safely cleanup to make sure that tests are
        starting from a clean state
        """
        try:
            backend_config = self._config.get('BACKEND_ENV', {})
            if backend_config:
                # create a repo even though we do not really need it since the config manager requires a repo for configurating the backend client
                # instances
                repo_info = ensure_test_repo(cli=j.clients.atyourservice.get().api.ays, repo_name=AYS_TESTRUNNER_REPO_NAME, logger=self._logger,
                                 config=self._config)
                if self._ovc_client is None:
                    _, self._ovc_client = configure_backend_clients(repo_info=repo_info, config=backend_config, logger=self._logger)
                # DELETE ALL THE CREATED CLOUDSPACES
                for cloudspace_info in self._ovc_client.api.cloudapi.cloudspaces.list():
                    self._ovc_client.api.cloudapi.cloudspaces.delete(cloudspaceId=cloudspace_info['id'])
                
                # DELETE TEST ACCOUNT
                if DEFAULT_ACCOUNT_NAME in self._ovc_client.accounts:
                    acc = self._ovc_client.account_get(name=DEFAULT_ACCOUNT_NAME, create=False)
                    acc.delete()
        except Exception as err:
            self._logger.error('Failed to execute cleanup. Error {}'.format(err))



    def _report_results(self):
        """
        Report final results after running all tests
        """
        nr_of_tests = len(self._tests)
        nr_of_failed = len(self._failed_tests)
        nr_of_ok = nr_of_tests - nr_of_failed
        print("AYS testrunner results\n---------------------------\n")
        print("Total number of tests: {}".format(nr_of_tests))
        print("Number of passed tests: {}".format(nr_of_ok))
        print("Number of failed/error tests: %s" % nr_of_failed)
        if self._failed_tests:
            print("Errors:\n")
            for test, job in self._failed_tests.items():
                header = 'Test {}'.format(test.name)
                print(header)
                print('-' * len(header))
                if test.errors:
                    print('\n'.join(test.errors))
                    print('\n')
                if hasattr(job, 'exc_info') and job.exc_info:
                    print(job.exc_info)
            raise RuntimeError('Failures while running ays tests')




class ThreadedTestRunner(BaseRunner):
    """
    Thread based testrunner
    """

    def run(self):
        """
        Run tests and report their results
        collects tests
        pre-process tests
        execute setup steps
        execute test
        execute teardown setps
        report tests
        """
        import threading
        try:
            jobs = {}
            self._tests = collect_tests(paths=self._config.get('bp_paths', self._default_bp_paths), logger=self._logger)
            self._pre_process_tests()
            for test in self._tests:
                self._logger.info('Scheduling test {}'.format(test.name))
                jobs[test] = threading.Thread(target=test.run, name=test.name)
                jobs[test].start()
                test.starttime = time.time()
            # block until all jobs are done
            while True:
                for test, job in jobs.copy().items():
                    self._logger.debug('Checking status of test {}'.format(test.name))
                    if job.is_alive():
                        self._logger.info('Test {} still running'.format(test.name))
                        if time.time() - test.starttime > self._config.get('TEST_TIMEOUT', DEFAULT_TEST_TIMEOUT):
                            self._logger.error('Test {} timed out'.format(test.name))
                            jobs.pop(test)
                            test.errors.append('Test {} timed out'.format(test.name))
                            self._failed_tests[test] = job
                    else:
                        if test.errors:
                            self._logger.error('Test {} failed'.format(test.name))    
                        else:
                            self._logger.info('Test {} completed successfully'.format(test.name))
                        jobs.pop(test)
                        test.endtime = time.time()
                if jobs:
                    time.sleep(10)
                else:
                    break

            # report final results
            self._report_results()
        finally:
            # clean up the BACKEND env if requested
            if self._config.get('BACKEND_ENV_CLEANUP', False):
                self._cleanup()



class ParallelTestRunner(BaseRunner):
    """
    Parallel process based test runner
    """
    def __init__(self, name, config=None):
        """
        Intialize test runner
        """
        super().__init__(name=name, config=config)
        self._task_queue = Queue(connection=Redis(), default_timeout=self._config.get('TEST_TIMEOUT', DEFAULT_TEST_TIMEOUT))


    def _collect_and_preprocess(self):
        """
        This is a workaround method that will be called from the run test scripts to avoid opening of the files during replacing the placeholders
        RQ is trying to pickle objects behind the scene and it fails if we open files in the same process.
        """
        self._tests = collect_tests(paths=self._config.get('bp_paths', self._default_bp_paths), logger=self._logger)
        if self._config.get('preprocess', True):
            self._pre_process_tests()


    def run(self):
        """
        Run tests and report their results
        collects tests
        pre-process tests
        execute setup steps
        execute test
        execute teardown setps
        report tests
        """
        try:
            jobs = {}
            self._collect_and_preprocess()
            for test in self._tests:
                self._logger.info('Scheduling test {}'.format(test.name))
                jobs[test] = self._task_queue.enqueue(test.run)
                test.starttime = time.time()
            # block until all jobs are done
            while True:
                for test, job in jobs.copy().items():
                    self._logger.debug('Checking status of test {}'.format(test.name))
                    if job.result is None:
                        self._logger.info('Test {} still running'.format(test.name))
                    elif job.result == []:
                        self._logger.info('Test {} completed successfully'.format(test.name))
                        jobs.pop(test)
                        test.endtime = time.time()
                    elif job.result is not None or job.exc_info is not None:
                        self._logger.error('Test {} failed'.format(test.name))
                        test.errors = job.result or [job.exc_info]
                        jobs.pop(test)
                        self._failed_tests[test] = job
                        test.endtime = time.time()
                if jobs:
                    time.sleep(10)
                else:
                    break

            # report final results
            self._report_results()
        finally:
            # clean up the BACKEND env if requested
            if self._config.get('BACKEND_ENV_CLEANUP', False):
                self._logger.debug('Cleaning up backend environment')
                self._cleanup()


class AYSCoreTestRunner(BaseRunner):
    """
    Test Runner to run ays core tets
    """

    def __init__(self, name, config=None):
        """
        Initialize core test runner
        """
        super().__init__(name=name, config=config)
        self._default_bp_paths = AYS_CORE_BP_TESTS_PATH



class AYSTestRunner(BaseRunner):
    """
    Test runner for non-core tests
    """

    def __init__(self, name, config=None):
        """
        Initialize non-core test runner
        """
        super().__init__(name=name, config=config)
        self._default_bp_paths = AYS_NON_CORE_BP_TESTS_PATH



class AYSCoreThreadedTestRunner(ThreadedTestRunner):
    """
    Test Runner to run ays core tets
    """

    def __init__(self, name, config=None):
        """
        Initialize core test runner
        """
        super().__init__(name=name, config=config)
        self._default_bp_paths = AYS_CORE_BP_TESTS_PATH



class AYSThreadedTestRunner(ThreadedTestRunner):
    """
    Test runner for non-core tests
    """

    def __init__(self, name, config=None):
        """
        Initialize non-core test runner
        """
        super().__init__(name=name, config=config)
        self._default_bp_paths = AYS_NON_CORE_BP_TESTS_PATH



class AYSCoreParallelTestRunner(ParallelTestRunner):
    """
    Test Runner to run ays core tets
    """

    def __init__(self, name, config=None):
        """
        Initialize core test runner
        """
        super().__init__(name=name, config=config)
        self._default_bp_paths = AYS_CORE_BP_TESTS_PATH



class AYSParallelTestRunner(ParallelTestRunner):
    """
    Test runner for non-core tests
    """

    def __init__(self, name, config=None):
        """
        Initialize non-core test runner
        """
        super().__init__(name=name, config=config)
        self._default_bp_paths = AYS_NON_CORE_BP_TESTS_PATH




class AYSTestRunnerFactory(object):
    """
    Factory class for creating aystestrunners
    """

    @staticmethod
    def get(name, execution_type='seq', test_type='core', config=None):
        if config is None:
            config = {}
        
        if execution_type == 'seq':
            if test_type == 'core':
                return AYSCoreTestRunner(name=name, config=config)
            else:
                return AYSTestRunner(name=name, config=config)
        elif execution_type == 'parallel':
            if test_type == 'core':
                return AYSCoreParallelTestRunner(name=name, config=config)
            else:
                return AYSParallelTestRunner(name=name, config=config)
        elif execution_type == 'threaded':
            if test_type == 'core':
                return AYSCoreThreadedTestRunner(name=name, config=config)
            else:
                return AYSThreadedTestRunner(name=name, config=config)
        else:
            raise ValueError('Invalid value for execution_type {}, allowed values are [seq, parallel, threaded]'.format(execution_type))

"""
Test runner module for AYS9

How to use it:
from ays_testrunner.testrunner import AYSCoreTestRunner
backend_config = {'URL': 'du-conv-2.demo.greenitglobe.com', 'LOGIN': 'aystestrunner@itsyouonline', 'PASSWORD': 'aystestrunner', 'ACCOUNT': 'aystestrunner', 'LOCATION': 'du-conv-2'}
core = AYSCoreTestRunner('core', config={'bp_paths': ['/root/gig/code/github/jumpscale/ays9/tests/bp_test_templates/core/test_auto_behavior.yaml', "/tmp/grouptest"], 'BACKEND_ENV': backend_config,
'TEST_TIMEOUT': 300})
core.run()
"""
from js9 import j
import os
import random
from redis import Redis
from rq import Queue
import logging
import time

AYS_CORE_BP_TESTS_PATH = [j.sal.fs.joinPaths(j.sal.fs.getParent(j.sal.fs.getParent(__file__)), 'tests', 'bp_test_templates', 'core')]

AYS_NON_CORE_BP_TESTS_PATH = [j.sal.fs.joinPaths(j.sal.fs.getParent(j.sal.fs.getParent(__file__)), 'tests', 'bp_test_templates', 'basic'),
                              j.sal.fs.joinPaths(j.sal.fs.getParent(j.sal.fs.getParent(__file__)), 'tests', 'bp_test_templates', 'advanced'),
                              j.sal.fs.joinPaths(j.sal.fs.getParent(j.sal.fs.getParent(__file__)), 'tests', 'bp_test_templates', 'extend')]

# AYS_DEFAULT_PLACEHOLDERS = ['URL', 'LOGIN', 'ACCOUNT', 'PASSWORD', 'LOCATION']
AYS_TESTRUNNER_REPO_NAME = 'ays_testrunner'
AYS_TESTRUNNER_REPO_GIT = 'https://github.com/ahussein/ays_testrunner.git'
DEFAULT_TEST_TIMEOUT = 600 # 10 min timeout per test

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

def ensure_test_repo(cli, repo_name, logger=None):
    """
    Ensure a new repo for running tests is created with unique name
    """
    if logger is None:
        logger = j.logger.logging

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
            result = ensure_test_repo(cli, repo_name)
        else:
            # create repo with that name
            res, ok = check_status_code(cli.createRepository(data={'name': repo_name, 'git_url': AYS_TESTRUNNER_REPO_GIT}), 201)
            if ok is True:
                result = res.json()
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
                                msg = 'Actor: {} Action: {}'.format(job['actor_name'], job['action_name'])
                                errors.append('\n%s' % msg)
                                errors.append('%s\n' % ('-' * len(msg)))
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
                        msg = 'Service role: {} Service instance: {}'.format(service_info['role'], service_info['name'])
                        errors.append('\n%s' % msg)
                        errors.append('%s\n' % ('-' * len(msg)))
                        errors.append(service_details['data']['result'])
                else:
                    errors.append('Failed to get service [{}!{}]'.format(service_info['role'], service_info['name']))
        else:
            errors.append('Failed to list services')
    else:
        errors.append('Failed to list runs')

    return errors

def collect_tests(paths, logger=None, setup=None, teardown=None):
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
            result.append(AYSTest(name=name, path=path))
            continue
        for dir_ in j.sal.fs.listDirsInDir(path):
            logger.debug('Creating group test for path {}'.format(dir_))
            result.append(AYSGroupTest(name=j.sal.fs.getBaseName(dir_), path=dir_))
        for file_ in sorted([file__ for file__ in j.sal.fs.listFilesInDir(path) if not j.sal.fs.getBaseName(file__).startswith('_') and
                                                                                  (file__.endswith('{}yaml'.format(os.path.extsep)) or
                                                                                  file__.endswith('{}bp'.format(os.path.extsep)))]):
            logger.debug('Creating test for path {}'.format(file_))
            result.append(AYSTest(name=j.sal.fs.getBaseName(file_), path=file_, setup=setup, teardown=teardown))
    return result


class AYSGroupTest:
    """
    Represet a group of test bps that depend on each other
    These tests will be executed in order(based on the file name)
    """
    def __init__(self, name, path, logger=None):
        """
        Initialize group test

        @param name: Name of the group
        @param path: Path to the hosting folder of the test bps
        @param logger: Logger object to use for logging
        """
        self._name = name
        self._path = path
        self._errors = []
        if logger is None:
            # FIXME: problem with using the js logger when pickling the object
            # self._logger = j.logger.get('aystestrunner.AYSTest.{}'.format(name))
            self._logger = logging.getLogger()
        else:
            self._logger = logger
        self._tests = collect_tests(paths=[path], logger=self._logger, setup=self.setup, teardown=self.teardown)


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

    def setup(self):
        """
        Setup steps
        """
        pass


    def teardown(self):
        """
        Teardown steps
        """
        try:
            for test in self._tests:
                test.teardown()
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

        self.teardown()
        return self._errors



class AYSTest:
    """
    Represents an AYS test bp
    """
    def __init__(self, name, path, logger=None, setup=None, teardown=None):
        """
        Initialize the test

        @param name: Name of the test
        @param path: Path to the test bp
        @param logger: Logger object to use for logging
        @param setup: Setup function to be called before the test
        @param teardown: Teardown function to be called after the test
        """
        self._path = path
        self._name = name
        self._prefab = j.tools.prefab.local
        self._repo_info = {}
        self._errors = []
        self._cli  = None
        self._starttime = None
        self._endtime = None
        if setup is None:
            self._setup = self.setup
        if teardown is None:
            self._teardown = self.teardown

        if logger is None:
            # FIXME: problem with using the js logger when pickling the object
            # self._logger = j.logger.get('aystestrunner.AYSTest.{}'.format(name))
            self._logger = logging.getLogger()
        else:
            self._logger = logger

        # create a repo per test
        try:
            self._cli = j.clients.atyourservice.get().api.ays
            self._repo_info = ensure_test_repo(self._cli, AYS_TESTRUNNER_REPO_NAME, logger=self._logger)
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
        sed_base_command = 'sed -i s/\<{key}\>/{value}/g {path}'
        self._logger.info('Replacing placeholders for test blueprint {}'.format(self._path))
        for item, value in config.items():
            cmd = sed_base_command.format(key=item, value=value, path=self._path)
            self._prefab.core.run(cmd)


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
                # self._cli.deleteRepository(repository=self._repo_info['name'])
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
        self.setup()

        try:
            if self._repo_info is None:
                self._errors.append('Failed to create new ays repository for test {}'.format(self._name))
            else:
                j.sal.fs.copyFile(self._path, j.sal.fs.joinPaths(self._repo_info['path'], 'blueprints', self._name))
                # execute bp
                self._errors.extend(execute_blueprint(self._cli, self._name, self._repo_info, logger=self._logger))
                if not self._errors:
                    # create run and execute it
                    self._errors.extend(create_run(self._cli, self._repo_info, logger=self._logger))
                    # report run
                    self._errors.extend(report_run(self._cli, self._repo_info, logger=self._logger))
        except Exception as err:
            self._errors.append('Test {} failed withe error: {}'.format(self._name, err))

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

        self._logger = j.logger.get('aystestrunner.{}'.format(name))
        # check if config is a file, then load cofnig from the file
        self._config = self._check_config(config)
        self._name = name
        self._task_queue = Queue(connection=Redis(), default_timeout=self._config.get('TEST_TIMEOUT', DEFAULT_TEST_TIMEOUT))
        self._failed_tests = {}
        self._tests = []

        self._default_bp_paths = []


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
        raise NotImplementedError("Not Implemented")


    def _check_config(self, config):
        """
        Check if config is file the it will try to read it as a json file
        """
        new_config = {}
        try:
            if type(config) is str:
                if j.sal.fs.exists(config):
                    new_config = json.load(open(config))
                else:
                    logger.warning('Config file {} does not exist. Default values will be used'.format(config))
            else:
                new_config = config
        finally:
            return new_config or {}

class AYSCoreTestRunner(BaseRunner):
    """
    Test Runner to run ays core tets
    """

    def __init__(self, name, config=None):
        """
        Initialize core test runner
        """
        super().__init__(name, config)
        self._default_bp_paths = AYS_CORE_BP_TESTS_PATH


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
            self._tests = collect_tests(paths=self._config.get('bp_paths', self._default_bp_paths), logger=self._logger)
            self._pre_process_tests()
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
                self._cleanup()


    def _cleanup(self):
        """
        Will clean up a BACKEND environment. Typically should be called for test environment where all the resources created can be safely cleanup to make sure that tests are
        starting from a clean state
        """
        try:
            backend_config = self._config.get('BACKEND_ENV', {})
            if backend_config:
                ovc_cli = j.clients.openvcloud.get(url=backend_config.get('URL'), login=backend_config.get('LOGIN'), password=backend_config.get('PASSWORD'))
                # DELETE ALL THE CREATED CLOUDSPACES
                for cloudspace_info in ovc_cli.api.cloudapi.cloudspaces.list():
                    ovc_cli.api.cloudapi.cloudspaces.delete(cloudspaceId=cloudspace_info['id'])
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
            for test, failed_test in self._failed_tests.items():
                header = 'Test {}'.format(test.name)
                print(header)
                print('-' * len(header))
                if failed_test.result:
                    print('\n'.join(failed_test.result))
                if failed_test.exc_info:
                    print(failed_test.exc_info)
            raise RuntimeError('Failures while running ays tests')


class AYSTestRunner(AYSCoreTestRunner):
    """
    Test runner for non-core tests
    """

    def __init__(self, name, config=None):
        """
        Initialize non-core test runner
        """
        super().__init__(name=name, config=config)
        self._default_bp_paths = AYS_NON_CORE_BP_TESTS_PATH

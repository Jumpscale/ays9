# AYS Testrunner Module
AYS has its own small test runner module that is responsible for running tests and reporting results during the build process of the framework.

## What is an AYS test
AYS test is a normal ays blueprint, ays blueprints are used as a basic unit for testing by defining test services.

## Types of tests
AYS tests consists of two kind of tests
- Core tests : These are blueprints that test the core functionalities of ays e.g: parsing blueprints, scheduling actions...
core tests can be found under https://github.com/Jumpscale/ays9/tree/master/tests/bp_test_templates/core
- Non-Core tests : There are blueprints that test the provided templates e.g: creating a virtual machine template..
non-core tests can be found under:
  - https://github.com/Jumpscale/ays9/tree/master/tests/bp_test_templates/basic
  - https://github.com/Jumpscale/ays9/tree/master/tests/bp_test_templates/advaced
  - https://github.com/Jumpscale/ays9/tree/master/tests/bp_test_templates/extend

## Execution Types of tests:
We have different types of executions for running the ays tests, these types are:
- Sequential: Runs the tests sequantially, good for debuging purposes, can be very slow when running non-core tests.
- Threaded: Runs the tests in parallel using separate thread for each tests.
- Parallel: Runs the tests in parallel using different processes (workers), requires installing rq pacakge.

## Prerequisites
To be able to use the test runner, you will need
- A running AYS server
- An installed rq package (only for Parallel execution type)

## Features
Test runner's main purpose is to be able to run tests and report their result, in addition to this it provides the following features
- Run tests in parallel
- Replace placeholders in test blueprints using a configuration dictionary passed to the runner at creation time
- Group tests that need to run sequentially 

## Configurations
When creating an instance of a test runner you can pass a configuration dictionary, the runner will support the following keys in the configuration dictionary
- bp_paths: this will allow you to specifiy a specific list of paths for tests to be collected from, each element of the list can be 
a path to a blueprint file or a path to a directory that contian blueprints.
- BACKEND_ENV: this show contian all the key the that you want to be replaced in the blueprints before running them. Each key in this
dictionary will be searched for in the test blueprints as <KEY> and if found then it will be replaced with the value provided.
- TEST_TIMEOUT: this sets the timeout value per test in seconds (default to 600)
- BACKEND_ENV_CLEANUP: this will clean up the backend env if set to True

If you create the a core test runner then the bp_paths will default to the core tests path and if you create a non-core test runner 
then the bp_paths will default to the non-core test paths.

## Tests collection
Collecting tests is based on the bp_paths configuration item. for each item in the bp_paths list we check
- If the item is a path to an existing blueprint (a file that ends with .bp or .yaml) then we create a test object for it.
- If the item is a path to an existing directory, then a test object will be created for each existing blueprint in that directory
and for each subdirectory, a group test object will be created.

## How to use it
### How to run core tests
#### Sequentially
```python
from ays_testrunner.testrunner import AYSTestRunnerFactory
runner = AYSTestRunnerFactory.get(name='core')
runner.run()
```
This will run all tests under https://github.com/Jumpscale/ays9/tree/master/tests/bp_test_templates/core sequentially

#### In Parallel (threaded)
```python
from ays_testrunner.testrunner import AYSTestRunnerFactory
runner = AYSTestRunnerFactory.get(name='core', execution_type='threaded')
runner.run()
```
This will run all tests under https://github.com/Jumpscale/ays9/tree/master/tests/bp_test_templates/core in parallel using threads

#### In Parallel (processes)
You need to have rq workers started already in a different process before to be able to process the testing jobs.
You can start rq workers using the following command:
```bash
js9 "for index in range(10): j.tools.prefab.local.tmux.executeInScreen('workers', 'rqworker{}'.format(index), cmd='rq worker', wait=0)"
```

Then you can run the tests using:
```python
from ays_testrunner.testrunner import AYSTestRunnerFactory
runner = AYSTestRunnerFactory.get(name='core', execution_type='parallel')
runner.run()
```
This will run all tests under https://github.com/Jumpscale/ays9/tree/master/tests/bp_test_templates/core in parallel using child processes and queues


### How to run non-core tests
```python
from ays_testrunner.testrunner import AYSTestRunnerFactory
backend_config = {'URL': 'du-conv-2.demo.greenitglobe.com', 'LOGIN': 'aystestrunner@itsyouonline', 'PASSWORD': '******', 'ACCOUNT': 'aystestrunner', 'LOCATION': 'du-conv-2'}
runner = AYSTestRunnerFactory.get(name='non-core', test_type='non-core', config={'BACKEND_ENV': backend_config, 'BACKEND_ENV_CLEANUP': True})
runner.run()
```
This will run all non-core tests in sequence, to run in a different execution mode use the execution_mode parameter as mentioned above

### How to run specific tests
```python
from ays_testrunner.testrunner import AYSTestRunnerFactory
runner = AYSTestRunnerFactory.get(name='custom', config={'bp_paths': [path to test1, path to test2, path ot dir1]})
runner.run()
```

### How to group tests
To group tests that depend on each other or user the same test repo for example then you need to create a directory under your test
folder and include the test blueprints in that directory with the correct naming to make sure order of execution.
An example for such grouping can be found under https://github.com/Jumpscale/ays9/tree/master/tests/bp_test_templates/core
there you can find an actions_delete folder that contains two tests that will run sequentially.

### How to skip tests
To skip a test in a test directory then you need to prefix the test with an '_' for example in the core tests that can 
be found under https://github.com/Jumpscale/ays9/tree/master/tests/bp_test_templates/core the test _test_validate_ays_update.yaml will no be executed.

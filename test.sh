#!bin/bash
set -e

RUNTYPE=$1


js9 'j.clients.redis.get4core() or j.clients.redis.start4core()'

echo "Starting AYS server"
js9 'j.atyourservice.server.start(dev=True)'

# sleep for 30 seconds
sleep 30

# check if the server started
js9 'cli=j.clients.atyourservice.get();cli.api.ays.listRepositories()'

# validate all the schemas
echo "Validating Schemas"
for schema in $(find -name schema.capnp); do
  echo "Validating $schema"
  capnp compile -oc++ $schema
done

# run rq workers
echo "Starting RQ workers"
js9 "for index in range(10): j.tools.prefab.local.system.tmux.executeInScreen('main', 'rqworker{}'.format(index), cmd='rq worker', wait=0)"


# running testsuite
echo "Running ays core tests"
js9 "from ays_testrunner.testrunner import AYSTestRunnerFactory;AYSTestRunnerFactory.get(name='core', execution_type='threaded').run()"

if [ -n $RUNTYPE ] && [ $RUNTYPE == "cron" ]; then
  echo "Running ays non-core tests"
  js9 "from ays_testrunner.testrunner import AYSTestRunnerFactory;import json;AYSTestRunnerFactory.get(name='none-core', execution_type='threaded', config={'BACKEND_ENV_CLEANUP': True, 'BACKEND_ENV': dict([(key.replace('BACKEND_', ''), value) for key, value in json.load(open('/hostcfg/ays_testrunner.json'))['BACKEND_ENV'].items()])}).run()"
fi




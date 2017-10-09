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

# running testsuite
echo "Running ays core tests"
js9 "from ays_testrunner.testrunner import AYSTestRunnerFactory;runner = AYSTestRunnerFactory.get(name='core', execution_type='threaded', config='/hostcfg/ays_testrunner.json').run()

if [ -n $RUNTYPE ] && [ $RUNTYPE == "cron" ]; then
  echo "Running ays non-core tests"
  js9 "from ays_testrunner.testrunner import AYSTestRunnerFactory;runner = AYSTestRunnerFactory.get(name='none-core', execution_type='threaded', test_type='non-core', config='/hostcfg/ays_testrunner.json').run()"
fi

#!bin/bash
set -e

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
js9 "for index in range(10): j.tools.prefab.local.tmux.executeInScreen('main', 'rqworker{}'.format(index), cmd='rq worker', wait=0)"


# running testsuite
echo "Running ays tests"
js9 "from ays_testrunner.testrunner import AYSCoreTestRunner;AYSCoreTestRunner(name='core').run()"

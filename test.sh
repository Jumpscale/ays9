#!bin/bash

echo "Starting AYS server"
js9 'j.atyourservice.server.start()'

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
echo "Running ays tests"
js9 "import testrunner; testrunner.main()"

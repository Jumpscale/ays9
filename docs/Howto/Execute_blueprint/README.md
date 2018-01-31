# How to Execute a Blueprint

Executing a blueprint means that you will instantiate all service instances as described in the blueprint.

You can execute a blueprint in three ways:

- [Using the AYS command line tool](#cli)
- [Using the AYS RESTful API](#rest)
- [Using the AYS Python client](#python)
- [Using the JumpScale client](#using-the-jumpScale-client)
- [Using the AYS Portal](#portal)

<a id="cli"></a>
## Using AYS command line tool

Once you've created a new AYS repository, as documented in [How to Create a New Repository](../Create_repository/README.md), a new directory will have been created that contains two empty subdirectories:
- `blueprints`
- `actorTemplates`

```bash
REPO_NAME="..."
cd $REPO_NAME
```

In order to execute a blueprint, you first need to create the blueprint, as documented in [How to Create Blueprints](../Create_blueprint/README.md).

Once you add your first blueprint, and execute it, two more directories will be created:

- `actors` containing the actor template files:
  - `actions.py`: Python code implementing the actions
  - `actor.json`: template for the AYS service state of each action
  - `schema.capnp`: schema of the AYS service
- `services` containing the actual state (files) for each AYS service (in a subdirectory):
  - `data.json`: information of the AYS service, as set through the blueprint
  - `schema.capnp`: schema of the AYS service
  - `service.json`: the state of each of the actions


<a id="rest"></a>
## Using the AYS RESTful API

In order to use the AYS RESTful API you first need to obtain an JWT, as documented in the section about [how to get a JWT](../Get_JWT/README.md).

Once you got the JWT, you can execute a blueprint:

```bash
curl -H "Authorization: bearer JWT"  /  
     https://BASE_URL/api/ays/repository/REPOSITORY-NAME/blueprint/BLUEPRINT-NAME
```

For instance in order to execute the blueprint discussed in the section [How to create a blueprint](../Create_blueprint/README.md):

```bash
curl -H "Authorization: bearer JWT"  /  
     https://BASE_URL/api/ays/repository/REPOSITORY-NAME/blueprint/user1.yaml
```

> Note that once executed the user still is not created. One more step is required, that is executing the install action on the user1 service instance, as documented in the section [How to install a service](Install_service/Install_service.md).


<a id="python"></a>
## Using the AYS Python client

Make sure the Python client is installed, as documented in [Install the Python Client](../../gettingstarted/python.md)

```python
from aysclient.client import Client
cl = Client("http://<IP address of your AYS server>:5000")

blueprint = "g8client__cl:\n  instance: main\n  account: 'Account of Yves'\nvdc__test_vdc1:\n  g8client: 'cl'\n  location: 'be-gen-1'\nactions:\n  - action: install"

data = {'name': 'test.yaml', 'content':blueprint}

rv = cl.ays.createBlueprint(data, "test_repo3")

rv = cl.ays.executeBlueprint("", "test.yaml", "test_repo3")

list = cl.ays.listServices("test_repo3")

list.json()

```

## Using the JumpScale client

Same code as above, but access the client in `j.clients.atyourservice`:
```python
cl = j.clients.atyourservice.get()
cl.api.ays.listRepositories().json()
...
```

<a id="portal"></a>
## Using the AYS Portal

This requires a running instance of the AYS Portal, as documented in [Start the AYS Portal](../../gettingstarted/portal.md).

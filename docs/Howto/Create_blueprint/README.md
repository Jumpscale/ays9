# How to Create a Blueprint

You can create a blueprint in multiple ways:

- [Using the AYS command line tool](#using-the-ays-command-line-tool)
- [Using the AYS RESTful API](#using-the-ays-restful-api)
- [Using the AYS Python client](#using-the-ays-python-client)
- [Using the JumpScale client](#using-the-jumpscale-client)
- [Using the AYS Portal](#using-the-ays-portal)

All are discussed here below.

Make sure to validate your blueprint first to have valid YAML format using a tool like [YAML Lint](http://www.yamllint.com/).


## Using the AYS command line tool

In order to creating a blueprint you need to have repository, creating repositories is discussed in [How to Create Repositories](../Create_repository/README.md).

```bash
vi blueprints/blueprint.yaml
```


## Using the AYS RESTful API

@todo needs review

In order to use the AYS RESTful API you first need to obtain an JWT, as documented in the section about [how to get a JWT](../Get_JWT/README.md).

Once you got the JWT, you can create a blueprint, for instance here below for creating a new user "mike" on gig.demo.greenitglobe.com:

```bash
curl -H "Authorization: bearer JWT"  /
     -H "Content-Type: application/json" /
     -d '{"name":"user1.yaml","content":"ovc_user__user1:\n  g8.client.name: 'gig'\n  username: 'mike'\n  email: 'mike@gmail.com'\n  provider: 'itsyouonline'"}'
     https://BASE_URL/ays/repository/REPO_NAME/blueprint/
```

> Note that the above blueprint will not create the user. Two more steps are are required for that, first execute the blueprint and then install the user, respectively documented in the sections [How to execute a blueprint](../Execute_blueprint/Execute_blueprint.md) and [How to install a service](Install_service/Install_service.md).



## Using the AYS Python client

Make sure the Python client is installed, as documented in [Install the Python Client](../../gettingstarted/python.md)

```python
from aysclient.client import Client
cl = Client("http://<IP address of your AYS server>:5000")

cl.ays...
```

## Using the JumpScale client

```python
cl = j.clients.atyourservice.get()
cl.api.ays.listRepositories().json()
...
```


## Using the AYS Portal

This requires a running instance of the AYS Portal, as documented in [Start the AYS Portal](../../gettingstarted/portal.md).

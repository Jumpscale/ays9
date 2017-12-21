## How to install a service

Before installing a service instance, make sure it is initialized, typically accomplished by executing the blueprint describing the blueprint, see the section about [how to execute a blueprint](../Execute_blueprint/Execute_blueprint.md).

You can install a service instance in multiple ways:

- [Using the Telegram Chatbot](#telegram)
- [In the Cockpit Portal](#portal)
- [Using the Cockpit API](#api)
- [At the CLI](#cli)

<a id="telegram"></a>
### Using the Telegram Chatbot

@todo


<a id="portal"></a>
### Using the Cockpit Portal

See the [Getting started with blueprints](../../Getting_started_with_blueprints/Getting_started_with_blueprints.md) section.


<a id="api"></a>
### Using the Cockpit API

In order to use the Cockpit API you first need to obtain an JWT, as documented in the section about [how to get a JWT](../Get_JWT/Get_JWT.md).

Once you got the JWT, you can install a service instance:

```
curl -H "Authorization: bearer JWT"  /
     -d "action=install&async=true&force=false&instance=INSTANCE-NAME&role=ROLE"
     https://BASE_URL/api/ays/repository/REPOSITORY-NAME/execute
```

So for instance to install the user as described in the blueprint documented in the sections [How to create a blueprint](../Create_blueprint/Create_blueprint.md) and [How to execute a blueprint](../Execute_blueprint/Execute_blueprint.md):

```
curl -H "Authorization: bearer JWT"  /
     -d "action=install&async=true&force=false&instance=user1&role=ovc_user"
     https://BASE_URL/api/ays/repository/REPOSITORY-NAME/execute
```

> In order to uninstall the user, check the section about [How to uninstall a service](../Uninstall_service/Uninstall_service.md).

Also see the section about the [API Console](../../API_Console/API_Console.md)

<a id="cli"></a>
### At the CLI

@todo

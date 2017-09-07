## REST API

The Cockpit exposes its functionality through a REST API.

The REST interface is generated from a [RAML](http://raml.org/) specification using [go-raml](https://github.com/jumpscale/go-raml). The RAML file is located at https://raw.githubusercontent.com/Jumpscale/jscockpit/master/ays_api/specifications/api.raml

The REST API is documented in the **API Console** of your portal. See the section about the [API Console](../API_Console/API_Console.md) for more information.


### API Client

Go-raml also supports generation of the client for an API.
[JumpScale](https://github.com/Jumpscale/jumpscale_core8) makes it even more user-friendly.


### How to use the Python client

The REST API of the Cockpit uses [JWT](https://jwt.io/) to authenticate requests.

See the section about [how to generate JWT tokens](../JWT/JWT.md).

Once you have your JWT token, usage of the client is trivial:

```python
jwt = '...JWT from cockpit portal...'
base_url = 'https://my-cockpit.com/api'
client = j.clients.cockpit.getClient(base_url, jwt)
```

List of available methods in the client:
```
ccl.addTemplateRepo     ccl.createRun           ccl.executeAction       ccl.getRun              ccl.listRepositories    ccl.listServicesByRole  ccl.updateBlueprint
ccl.archiveBlueprint    ccl.deleteBlueprint     ccl.executeBlueprint    ccl.getServiceByName    ccl.listRuns            ccl.listTemplates       ccl.updateCockpit
ccl.createNewBlueprint  ccl.deleteRepository    ccl.getBlueprint        ccl.getTemplate         ccl.listServiceActions  ccl.restoreBlueprint
ccl.createNewRepository ccl.deleteServiceByName ccl.getRepository       ccl.listBlueprints      ccl.listServices        ccl.simulateAction
```

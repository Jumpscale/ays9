# How to Create a VDC

For creating a virtual datacenter (VDC) use the **vdc** template, available here: https://github.com/Jumpscale/ays9/tree/master/templates/ovc/vdc

- [Minimal Blueprint](#minimal-blueprint)
- [Full Blueprint](#full-blueprint)
- [Values](#values)
- [Example](#example)
- [Using the AYS command line tool](#cli)
- [Using the AYS RESTful API](#rest)
- [Using the AYS Python client](#using-the-python-client)
- [Using the JumpScale client](#using-the-jumpscale-client)
- [Using the AYS Portal](#using-the-ays-portal)

## Minimal Blueprint

```yaml
g8client__{environment}:
  url: '{url}'
  login: '{login}'
  password: '{password}'
  account: '{account}'

vdc__{vdc-name}:
  g8client: '{environment}'
  location: '{location}'

actions:
  - action: install  
```


## Full blueprint

The full blueprint includes additional sections for following AYS templates:
- `uservdc` for creating and/or granting user access to accounts and/or the VDCs
- `vdcfarm` for logically grouping VDCs, if omitted a default `vdcfarm` service will be created implicitly
- `account` for setting account limitations and control access to this account
  - If you only specify an `account` in the `g8client` section (and optionally in the `vdc`) section, thus not explicitly including any `account` sections in the blueprint, then an `account` service will be created implicitly with the specified account name
  - Explicitly including an `account` section allows you to create a new account and/or grant and revoke user access to the specified account, for more details see [Create a New OpenvCloud Account](../Create_account/README.md) and [Manage Account User Access](../Manage_account_user_access/README.md)


```yaml
g8client__{environment}:
  url: '{url}'
  login: '{login}'
  password: '{password}'
  account: '{account}'

uservdc__{username1}:
  g8client: '{environment}'
  email: '{email1}'
  provider: 'itsyouonline'

uservdc__{username2}:
  g8client: '{environment}'
  email: '{email2}'
  provider: 'itsyouonline'

vdcfarm__{vdcfarm}:

account__{account}:
  description: '{description}'
  g8client: '{environment}'
  accountusers:
    - {username1}
    - {username2}
  maxMemoryCapacity: {maxMemoryCapacity}
  maxCPUCapacity: {maxCPUCapacity}
  maxDiskCapacity: {maxDiskCapacity}
  maxNumPublicIP: {maxNumPublicIP}

vdc__{vdc-name}:
  description: '{description}'
  vdcfarm: '{vdcfarm}'
  g8client: '{environment}'
  account: '{account}'
  location: '{location}'
  externalNetworkID: `{externalNetworkID}`
  uservdc:
    - `{username1}`
    - `{username2}`
  maxMemoryCapacity: {maxMemoryCapacity}
  maxCPUCapacity: {maxCPUCapacity}
  maxDiskCapacity: {maxDiskCapacity}
  maxNumPublicIP: {maxNumPublicIP}

actions:
  - action: install   
```

## Values

- `{environment}`: OpenvCloud environment name for referencing elsewhere in the same blueprint or other blueprint in the repository
- `{url}`: URL to the environment, e.g. `gig.demo.greenitglobe.com`
- `{login}`: username on the OpenvCloud user
- `{password}`: password for the OpenvCloud user
- `{account}`: OpenvCloud account name
- `{username1}` and `{username2}`: ItsYou.online usernames
- `{email1}` and `{email1}`: email addresses of the ItsYou.online users
- `{vdc-name}`: name of the VDC that will be created, and if a VDC with the specified name already exists then that VDC will be used
- `{description}`:  optional description for an account or VDC
- `{vdcfarm}`: optional name of the VDC farm to logically group VDCs; if not specified a new VDC farm will be created
- `{location}`: location where the VDC needs to be created
- `{externalNetworkID}`: ID of the external network to which the VDC needs to get connected; of not specified then it will default to the first/default external network
- `{maxMemoryCapacity}`: available memory in GB for all virtual machines in the VDC or account
- `{maxCPUCapacity}`: total number of available virtual CPU core that can be used by the virtual machines in the VDC or account
- `{maxDiskCapacity}`: available disk capacity in GiB for all virtual disks in the VDC or account
- `{maxNumPublicIP}`: number of external IP addresses that can be used by the VDC or account

> Note that you can specify an account both in `g8client` and in `vdc`, you have basically 4 options:
> - Specify the account only in `g8client`, this will implicitly create an `account` service with that name
> - Specify the same account in both `g8client` and `vdc`
> - Specify a different account in both `g8client` and `vdc`, allowing you to deploy the VDC in another account than the one specified in `g8client`, this of course requires that the user has access to both accounts

Future attribute:
- `allowedVMSizes`: listing all IDs of the VM sizes that are allowed in this cloud space


Also possible:
Instead of providing a login and password for the g8client actor, you can also provide a JWT string: `jwt= type:str default:''``
See: https://github.com/Jumpscale/ays_jumpscale8/blob/8.1.1/templates/clients/g8client/schema.hrd


Return values:
cloudspaceID = type:int default:0
...


## Example

Here's an example blueprint for creating a VDC:

```yaml
g8client__cl:
  url: 'be-gen-1.demo.greenitglobe.com'
  login: '***'
  password: '***'
  account: 'demo'

vdc__myvdc:
  g8client: 'cl'
  location: 'be-gen-1'

actions:
  - action: install
```


<a id="cli"></a>
## Using the AYS command line tool

You first need to create an AYS repository, as documented in [How to Create a New Repository](../Create_repository/README.md).

Once created make the AYS directory of your repository the current directory:
```bash
REPO_NAME="..."
cd /host/var/cockpit_repos/$REPO_NAME
```

Create a blueprint:
```bash
VDC_NAME="..."
vi blueprint blueprints/$VDC_NAME.yaml
```

Provide following blueprint to create `vdc1` in the G8 environment identified by `env`:
```yaml
g8client__env:
  url: 'be-gen-1.demo.greenitglobe.com'
  login: '***'
  password: '***'
  account: '***'

vdc__vdc1:
  g8client: 'env'
  location: 'be-gen-1'

actions:
  - action: install
```

Have AYS process the new blueprint using the `ays blueprint` command.
```bash
ays blueprint
```

You can check the result using the `ays service list` command that will list all services:
```bash
ays service list
```

You will notice that there is a service `vdcfarm!auto_1` that is not defined in the blueprint. It is created implicitly for every new VDC if no VDC Farm was specified explicitly. A VDC Farm is an organizational AYS service for grouping VDC services.

Using the `ays service show` command you can see that the new VDC service is indeed a child of the auto-created `vdcfarm` service named `auto_1`.

```bash
ays service show -r vdc
```

The same can be seen when checking the `services` directory:
```bash
tree -A services

services
├── account!***
│   ├── data.json
│   ├── schema.capnp
│   └── service.json
├── g8client!cl
│   ├── data.json
│   ├── schema.capnp
│   └── service.json
└── vdcfarm!auto_1
    ├── data.json
    ├── schema.capnp
    ├── service.json
    └── vdc!vdc1
        ├── data.json
        ├── schema.capnp
        └── service.json
```

Using the `ays service state` command you can verify that `install` action of the VDC service is actually not yet executed, but rather `scheduled` to be executed, as indicated by the `scheduled` state next to the `install` action. So as a result of using the `ays blueprint` command only the `init` and `input` actions got executed successfully, indicated by `ok` next to these actions:
```bash
ays service state -r vdc

State of service : vdc!vdc1
        action_post_              : new
        action_pre_               : new
        check_down                : new
        check_requirements        : new
        check_up                  : new
        cleanup                   : new
        consume                   : new
        data_export               : new
        data_import               : new
        halt                      : new
        init                      : ok
        init_actions_             : new
        input                     : ok
        install                   : scheduled
        monitor                   : new
        processChange             : new
        removedata                : new
        start                     : new
        stop                      : new
        uninstall                 : new
```

The same is confirmed when you check the file `service.json` in the service directory:
```bash
vi services/vdcfarm\!auto_1/vdc\!vdc1/service.json
```

Here you see more detailed information, like for instance for the `install` action:

```json
{
 "actionKey":"921cc33036f00b3651188d236081a684",
 "errorNr":0,
 "isJob":true,
 "lastRun":0,
 "log":true,
 "name":"install",
 "period":0,
 "state":"ok",
 "timeout":0
}
```

The value for `lastRun` is 0 indicating that the `install` action has not yet run. In order to actually run the scheduled `install` action you need execute the `ays run create` command that will start a run for all actions that are in the `scheduled` state:
```bash
ays run create -f
```

Using the `-f` option allows you to *follow* synchronously the process.

To lists all runs use the `ays run list` command:
```bash
ays run list
```

To get the details for a run use the `ays run show` command specifying the run with `-k` option:
```bash
ays run show -k d1542eda4e69fca3989c8a11865a0172
```

To see the log for this run:
```bash
ays run show -k d1542eda4e69fca3989c8a11865a0172 --logs
```

In case an error condition is mentioned, and you've access to the Cloud Broker Portal, use following URL:
https://be-gen-1.demo.greenitglobe.com/grid/error%20condition?id=fdc34b88-db89-8367-a682-fd7c42d88a74

Also see logs in ``/host/var/log/`:
```bash
tail -f jumpscale.log
```

Once the VDC got installed successfully by a successful run of the `installed` action, you'll see a non-zero value next for `lastRun` when checking the `service.json` of :

```json
{
 "actionKey":"921cc33036f00b3651188d236081a684",
 "errorNr":0,
 "isJob":true,
 "lastRun":1495620203,
 "log":true,
 "name":"install",
 "period":0,
 "state":"ok",
 "timeout":0
}
```

The value for `lastRun` is non-zero, indicating that the `install` was already run. As a result, if you'd execute the blueprint again, or just another blueprint with only including the actions, it will not change the state of the `install` action to `scheduled`.

In order to force this anyhow, you'll need to execute an `actions` blueprint that uses the `force` option:

```bash
vi blueprints/actions.yaml
```

```yaml
actions:
  - action: install
    force: True
```

Or in order to only force a change for the vdc service:

```yaml
actions:
  - action: install
    actor: vdc
    service: vdc1
    force: True
```

Execute this new `actions.yaml`:
```bash
ays blueprint actions.yaml
```

Next you will want to learn about one of the following :
- How to [Create a VDC using the AYS API](#api) in the next section here below
- How to [Delete a VDC](../Delete_VDC/README.md)
- How to [Grant User Access to a VDC](..//README.md)
- How to [Change VDC Resource Limits](../Change_VDC_Resource_Limits/README.md)


<a id="rest"></a>
## Using the AYS RESTful API

With the below command we make AYS listen on port 5000 on all interface:

```
ays start -b 0.0.0.0 -p 5000
```

The AYS command line tool discussed here above is actually a client of the AYS API. In this section we discuss how to create a VDC step by step by interacting directly with the AYS API using curl commands:

- [Get an OAuth token with Client Credentials Flow](#get-token)
- [Get a JWT to talk to the Cockpit](#get-JWT)
- [Create a new repository](#create-repository)
- [List all repositories](#list-repositories)
- [Create blueprint for a g8client service instance](#g8client-blueprint)
- [Execute the g8client blueprint](#g8client-execute)
- [Create blueprint for a user](#user-blueprint)
- [Execute the user blueprint](#user-execute)
- [Create blueprint for new VDC](#vdc-blueprint)
- [Execute the VDC blueprint](#vdc-execute)
- [Start a run to actually deploy the VDC](#install-VDC)


<a id="get-token"></a>
### Get an OAuth token with Client Credentials Flow

```bash
CLIENT_ID="..."
CLIENT_SECRET="..."
curl -d "grant_type=client_credentials&client_id=${CLIENT_ID}&client_secret=${CLIENT_SECRET}" \
     https://itsyou.online/v1/oauth/access_token > token.txt
ACCESS_TOKEN=$(awk '{split($0,a,",");split(a[1],b,":");gsub(/\"/,"",b[2]);print b[2]}' token.txt)
echo $ACCESS_TOKEN
```

<a id="get-JWT"></a>
### Get a JWT to talk to the Cockpit

```bash
JWT=$(curl -H "Authorization: token ${ACCESS_TOKEN}" https://itsyou.online/v1/oauth/jwt?aud=${CLIENT_ID})
echo $JWT
```

<a id="list-repositories"></a>
### List all repositories

```bash
BASE_URL="<IP-address>"
AYS_PORT="5000"
curl -X GET \
     -H "Authorization: bearer $JWT" \
     -H "Content-Type: application/json" \
     https://$BASE_URL:$AYS_PORT/ays/repository
```

<a id="create-repository"></a>
### Create a new repository

```bash
REPO_NAME="..."
GIT_URL="http://somewhere"
curl -X POST \
     -H "Authorization: bearer $JWT" \
     -H "Content-Type: application/json" \
     -d '{"name":"'$REPO_NAME'", "git_url":"'$GIT_URL'"}' \
     https://$BASE_URL:$AYS_PORT/ays/repository
```

<a id="g8client-blueprint"></a>
### Create blueprint for a g8client service instance

```bash
G8_URL="..."
LOGIN="..."
PASSWORD="..."
ACCOUNT="..."
curl -X POST \
     -v \
     -H "Authorization: bearer $JWT" \
     -H "Content-Type: application/json" \
     -d '{"name":"cl.yaml","content":"g8client__cl:\n  url: '$G8_URL'\n  login: '$LOGIN'\n  password: '$PASSWORD'\n  account: '$ACCOUNT'"}' \
     https://$BASE_URL:$AYS_PORT/ays/repository/$REPO_NAME/blueprint
```

<a id="g8client-execute"></a>
### Execute the g8client blueprint

```bash
curl -X POST \
     -H "Authorization: bearer $JWT" \
     https://$BASE_URL:$AYS_PORT/ays/repository/$REPO_NAME/blueprint/cl.yaml
```

<a id="user-blueprint"></a>
### Create blueprint for a user

```bash
USERNAME="..."
EMAIL="..."
curl -H "Authorization: bearer $JWT" \
     -H "Content-Type: application/json" \
     -d '{"name":"'$USERNAME'.yaml","content":"uservdc__'$USERNAME':\n  g8.client.name: cl\n  username: '$USERNAME'\n  email: '$EMAIL'\n  provider: itsyouonline"}' \
     https://$BASE_URL:$AYS_PORT/ays/repository/$REPO_NAME/blueprint
```

<a id="user-execute"></a>
### Execute the user blueprint

```bash
curl -X POST \
     -H "Authorization: bearer $JWT" \  
     http://$BASE_URL:$AYS_PORT/ays/repository/$REPO_NAME/blueprint/$USERNAME.yaml
```

<a id="vdc-blueprint"></a>
### Create blueprint for new VDC

In order to create a VDC you need the name of the G8 location and the ID of the external network.

In order to get a list of available external networks for a given account use the Cloud API, here for account with ID=23:

```bash
curl -X POST \
     --header "Content-Type: application/x-www-form-urlencoded" \
     --header "Accept: application/json" \
     -d "accountId=23" \
     https://$BASE_URL/restmachine/cloudapi/externalnetwork/list
```

In order to get this list of available locations use the following Cloud API:

```bash
curl -X POST \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     https://be-gen-1.demo.greenitglobe.com/restmachine/cloudapi/locations/list
```

```bash
VDC_NAME="..."
LOCATION="..."
EXTERNAL_NETWORK="..."

curl -X POST \
     -H "Authorization: bearer $JWT" \
     -H "Content-Type: application/json" \
     -d '{"name":"'$VDC_NAME'.yaml","content":"vdc__'$VDC_NAME':\n  g8client: cl\n  location: '$LOCATION'\n  externalNetworkID: '$EXTERNAL_NETWORK'"}' \
     https://$BASE_URL:$AYS_PORT/ays/repository/$REPO_NAME/blueprint
```

<a id="vdc-execute"></a>
### Execute the VDC blueprint

```bash
curl -X POST \
     -H "Authorization: bearer $JWT" \
     https://$BASE_URL:$AYS_PORT/ays/repository/$REPO_NAME/blueprint/$VDC_NAME.yaml
```

<a id="vdc-execute"></a>
### Create a blueprint for calling the install actions

```bash
curl -X POST
     -H "Authorization: bearer $JWT" \
     -H "Content-Type: application/json" \
     -d '{"name":"actions.yaml","content":"actions:\n  - action: install\n"}' \
     https://$BASE_URL:$AYS_PORT/ays/repository/$REPO_NAME/blueprint
```


<a id="vdc-execute"></a>
### Execute the install actions blueprint

```bash
curl -X POST \
     http://$BASE_URL:$AYS_PORT/ays/repository/$REPO_NAME/blueprint/actions.yaml
```


<a id="install-VDC"></a>
### Start a run to actually deploy the VDC

```bash
curl -X POST \
     -H "Authorization: bearer $JWT" \
     http://$BASE_URL:$AYS_PORT/ays/repository/$REPO_NAME/aysrun | python -m json.tool
```


## Using the AYS Python client

Make sure the Python client is installed, as documented in [Install the Python Client](../../gettingstarted/python.md)

```python
from aysclient.client import Client
cl=Client("http://<IP address of AYS server>:5000")

blueprint = "g8client__cl:\n  url: 'be-gen-1.demo.greenitglobe.com'\n  login: 'api_user'\n  password: '***'\n  account: 'Account of Yves'\nvdc__test_vdc1:\n  g8client: 'cl'\n  location: 'be-gen-1'\nactions:\n  - action: install"

data = {'name': 'test.yaml', 'content':blueprint}

rv = cl.ays.createBlueprint(data, "test_repo3")

rv = cl.ays.executeBlueprint("", "test.yaml", "test_repo3")

run = cl.ays.createRun("", "test_repo3")

run.json()

list = cl.ays.listRuns("test_repo3")

list.json()

run = cl.ays.getRun("20d13bd535a31b4b4af6c0985d1f61f8", "test_repo3")

run.json()
```

## Using the JumpScale client

Same code as above,

```python
cl = j.clients.atyourservice.get()

list = cl.api.ays.listBlueprints("test_repo3")
list.json()

blueprint = cl.api.ays.getBlueprint("test.yaml", "test_repo3")
blueprint.json()

```

## Using the AYS Portal

This requires a running instance of the AYS Portal, as documented in [Start the AYS Portal](../../gettingstarted/portal.md).

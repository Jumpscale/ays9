# Use the AYS client

## Preparation

Use the Z-tools to install JS9: https://github.com/Jumpscale/bash

Installing the master branch of the Z-tools:
```bash
export ZUTILSBRANCH="master"
export ZBRANCH="master"
curl https://raw.githubusercontent.com/Jumpscale/bash/${ZUTILSBRANCH}/install.sh?$RANDOM > /tmp/install.sh;bash /tmp/install.sh
```

Make the bash tools available:
```bash
source ~/.bash_profile
```

Install:
```bash
ZInstall_js9_full
```

Install ZeroTier (optionally):
```bash
curl -s https://install.zerotier.com/ | sudo bash
```

Start ZeroTier daemon (optionally):
```bash
zerotier-one -d
```

Join ZeroTier network (optionally):
```bash
ZT_ID=""
zerotier-cli join $ZT_ID
```

## Get a JWT

In order to interact with AYS you will typically need a JWT, unless the RESTful API is not protected with ItsYou.online.

Options to get a JWT: https://github.com/Jumpscale/ays9/tree/master/docs/Howto/Get_JWT

First get/create an API key for the ItsYou.online organization used to protect you AYS server, and copy the name of the organization and the secret into environment variables:
```bash
CLIENT_ID="ays-organization"
SECRET=:"..."
```

Using the AYS RESTfull API:
```bash
JWT1=$(curl -d 'grant_type=client_credentials&client_id='"$CLIENT_ID"'&client_secret='"$SECRET"'&response_type=id_token' https://itsyou.online/v1/oauth/access_token)
echo $JWT1
```

Export JWT1 so you can access it from the JumpScale interactive shell:
```bash
export JWT1
```

Or alternativelly in Python:
```python
import os
import requests
params = {
  'grant_type': 'client_credentials',
  'client_id': os.environ['CLIENT_ID'],
  'client_secret': os.environ['SECRET'],
  'response_type': 'id_token',
  'scope': 'offline_access'
}
url = 'https://itsyou.online/v1/oauth/access_token'
resp = requests.post(url, params=params)
resp.raise_for_status()
jwt1 = resp.content.decode('utf8')
```

## Connect to a remote AYS server

Start the JumpScale interactive shell:
```bash
js9
```

Connect:
```python
import os
jwt1 = os.environ['JWT1']
base_uri = "http://172.25.0.238:5000"
cl = j.clients.ays.get(base_uri, jwt1)
```

## List all repositories

```python
cl.repositories.list()
```

Or alternativelly using the auto-generated client:
```python
repositories = cl._ayscl.listRepositories()
repositories.json()
```

## Create a repository

```python
repo = cl.repositories.create("tuesday-repo", "http://whatever")
```

Or alternativelly using the auto-generated AYS client:
```python
data = {'name': 'test99', 'git_url': 'http://whatever'}
resp = cl._ayscl.createRepository(data)
resp.json()
```

## Use a blueprint template
...

## Get JWT for interacting with the OpenvCloud API

Next to the JWT for interacting with the AYS server, you'll need a second JWT to pass in a blueprint for allowing AYS to interact with an OpenvCloud environment.

See: https://gig.gitbooks.io/ovcdoc_public/content/API/GettingStarted.html

Create an API key in your ItsYou.online profile, and copy the **Application ID** and **Secret** into environment variables: 
```bash
APP_ID="..."
SECRET2="..."
```

Optioanally, in order to make the environement variable available from the Python interactive shell:
```bash
export APP_ID
export SECRET2
```

Use curl to get a JWT
```bash
JWT2=$(curl -d 'grant_type=client_credentials&client_id='"$APP_ID"'&client_secret='"$SECRET2"'&response_type=id_token' https://itsyou.online/v1/oauth/access_token)
echo $JWT2
```

Again optionally, in order to make the JWT value available from the Python interactive shell:
```bash
export JWT2
```

## Create a blueprint for creating a VDC

Create a blueprint file:
```yaml
g8client__g8:
  url: 'be-gen-1.demo.greenitglobe.com'
  jwt: '<JWT2>'
  account: 'myaccount'

vdc__testvdc10:
  g8client: 'g8'
  location: 'be-gen-1'

actions:
  - action: install
```

Use an repository as created before/above:
```python
repo = cl.repositories.get("tuesday-repo")
```

Read blueprint from a file:
```python
file_name="vdc.yaml"
blueprint_file = open(file_name,'r')
blueprint = blueprint_file.read()
```

Create a blueprint:
```python
bp_name="vdc.yaml"
bp=repo.blueprints.create(bp_name, blueprint)
```

Close the file:
```python
blueprint_file.close()
```

Or use an existing blueprint:
```python
bp=repo.blueprints.get(bp_name)
```

Execute the blueprint:
```python
bp.execute()
```

Check created services:
```python
repo.services.list()
```

Create a run:
```pyton
key=repo.runs.create()
```

List all runs:
```python
repo.runs.list()
```

Check run:
```python
myrun=repo.runs.get(key)
myrun.model
```

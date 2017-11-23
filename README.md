![travis](https://travis-ci.org/Jumpscale/ays9.svg?branch=master)

[we are working on new version, there is zoom meeting available which explains why GIG](https://drive.google.com/drive/folders/1rsk5dGy1z4VMENRr9qv3LeJ7W2epwTMc)

# AYS

It is an application lifecycle management system for cloud infrastructure and applications and is installed as part of a JumpScale installation.

The AYS server automates the full lifecycle of the cloud infrastructure and applications it manages, from deployment, monitoring, scaling and self-healing to uninstalling.

For more information and how to use see [docs](docs/AYS-Introduction.md).

- [version & roadmap info](https://github.com/Jumpscale/home/blob/master/README.md)

## Installation
To install and use ays9 you need a JumpScale 9 installation. To install JumpScale follow the documentation [here](https://github.com/Jumpscale/bash/blob/master/README.md).

To install ays dependencies navigate to repo path and execute:
 - in the command-line
```bash
bash install.sh
```
or
 -  in the python shell of jumpscale ( js9 ):
```python
j.tools.prefab.local.apps.atyourservice.install()
```
### Installation from branch
To install from certain branch navigate to repo path and execute:
 - in the command-line
```bash
export JS9BRANCH={branch}
bash install.sh
```
or
 -  in the python shell of jumpscale ( js9 ):
```python
j.tools.prefab.local.apps.atyourservice.install(branch='{branch}')
```


To connect to a remote AYS server without installing JumpScale, it is possible to use the [AYS client](docs/gettingstarted/python.md).

For information about the AYS portal and how to load it to the [portal](https://github.com/Jumpscale/portal9) see [here](docs/AYS-Portal)

## OVC templates

To use OVC templates, which are templates used to perform various actions on OpenVCloud environments(like creating a cloudspace,vm, ...) you need to add the actor templates to your system.

This can be done by executing the following code in a js9 shell(type `js9` in the command line), in this instance it will clone from master:

```python
ayscl = j.clients.atyourservice.get()
ayscl.api.ays.addTemplateRepo(data={'url': 'https://github.com/openvcloud/ays_templates','branch': 'master'})

```

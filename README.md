![travis](https://travis-ci.org/Jumpscale/ays9.svg?branch=master)

# AYS

It is an application lifecycle management system for cloud infrastructure and applications and is installed as part of a JumpScale installation.

The AYS server automates the full lifecycle of the cloud infrastructure and applications it manages, from deployment, monitoring, scaling and self-healing to uninstalling.

For more information and how to use see [docs](docs/AYS-Introduction.md).

- [version & roadmap info](https://github.com/Jumpscale/home/blob/master/README.md)

## Installation
To install and use ays9 you need a JumpScale 9 installation. To install JumpScale follow the documentation [here](https://github.com/Jumpscale/developer/blob/master/README.md).

To install ays dependencies navigate to repo path and execute:
```bash
bash install.sh
```
To connect to a remote AYS server without installing JumpScale, it is possible to use the [AYS client](docs/gettingstarted/python.md).

For information about the AYS portal and how to load it to the [portal](https://github.com/Jumpscale/portal9) see [here](docs/AYS-Portal)

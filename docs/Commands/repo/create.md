# ays repo create

```shell
ays repo create [OPTIONS]

  create a new AYS repository

Options:
  -n, --name TEXT  name of the new AYS repo you want to create
  -g, --git TEXT   URL of the git repository to attach to this AYS repository
  --help           Show this message and exit.
```

Example usage :

```shell
$ ays repo create -n test -g http://github.com/user/ays_repo
AYS repository created at /host/var/ays_repos/test
```

If you added a git url that uses ssh, you will be able to auto push any changes at this repo by authorizing the key printed after creation of the repo

```bash
$ ays repo create -n test -g "git@github.com:user/ays_repo.git"
[Tue11 12:27] - SystemProcess.py    :661 :j.sal.process                  - INFO     - Checking whether at least 1 processes redis-server are running
AYS repository created at /host/var/ays_repos/gsdjsh
If you want to auto push AYS Repo changes, please authorize the following ssh key to your git repository: 
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDCxr...... root@js9

```
```toml
!!!
title = "AYS Repo Create"
tags= ["ays"]
date = "2017-03-02"
categories= ["ays_cmd"]
```

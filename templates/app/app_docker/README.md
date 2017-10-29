#template: app_docker

##Description:

This actor template installs docker and docker compose on parent os.

##Schema:
 - os: Parent os service name defined in blueprint. *Required*

##Example:

```yaml
sshkey__ovh_install:

node.physical__ovh4:
  ip.public: '172.17.0.2'
  ssh.login: 'root'
  ssh.password: '<root password>'
  ssh.addr: 'localhost'
  ssh.port: 22


os.ssh.ubuntu__ovh4:
  sshAddr: 'localhost'
  sshPort: 22
  sshkey: 'ovh_install'
  node: 'ovh4'

app_docker__dockerapp:
  #name of os on which we will install docker application
  os: 'ubuntu__ovh4'

```

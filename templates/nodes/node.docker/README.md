# template: node.docker

## Description:

This actor template represents a docker container , it is created through the install action.
The container is deleted through the uninstall action.
The container is started through the start action.
The container is stopped through the stop action.



## Schema:
 - os: Parent os service name defined in blueprint. *Required*
 - fs: files systems to use on container.
 - docker: app_docker service to use (To install docker on node).
 - hostname: hostname of created conatiner.
 - image: image used to run, default to ubuntu.
 - ports: port forwards to host machine.
 - volumes: files systems to mount on container.
 - cmd: init command to run on container start.
 - sshkey: add ssh key to container.
 - id: id of the container.
 - ipPublic: automatically set public ip.
 - ipPrivate: automatically set private ip.
 - sshLogin: username to login with.
 - sshPassword: password to login with.

## Example:
Replace \<with actual value \>
```yaml
sshkey__ovh_install:

node.physical__ovh4:
  ipPublic: '172.17.0.2'
  sshLogin: 'root'
  sshPassword: '<root password>'
  sshAddr: 'localhost'
  sshPort: 22


os.ssh.ubuntu__ovh4:
  sshAddr: 'localhost'
  sshPort: 22
  sshkey: 'ovh_install'
  node: 'ovh4'

node.docker__ubuntutest:
  sshkey: 'ovh_install'
  image: 'ubuntu'
  ports:
    - "80"
  os: 'ovh4'

os.ssh.ubuntu__docker_ovh4:
  sshkey: 'ovh_install'
  node: 'ubuntutest'

actions:
    - action: 'install'
```

If the specified node doesn't have docker installed, use `app_docker` template to install docker on the node and sepcify the service name in the `node.docker` service as follows:

```yaml
app_docker__dockerd:
  os: 'ovh4'

node.docker__ubuntutest:
  sshkey: 'ovh_install'
  image: 'ubuntu'
  ports:
    - "80"
  os: 'ovh4'
  docker: dockerd # Name of app_docker service

```

## Example OVC:
Replace \<with actual value \>
```yaml
g8client__g8:
  url: '<env url>'
  login: '<user name>'
  password: '<user password>'
  account: '<account name>'

vdc__myvdc:
  g8client: 'g8'
  location: '<env name>' # ex: du-conv-2

disk.ovc__disk1:
  size: 5
  type: "D"
  maxIOPS: 200

node.ovc__myvm:
  vdc: myvdc
  bootdisk.size: 50
  memory: 2
  os.image: 'Ubuntu 16.04 x64'
  ports:
    - '2210:22'
  disk:
    - 'disk1'

app_docker__dockerd:
  os: 'myvm'

node.docker__apache:
  image: 'bitnami/apache'
  ports:
    - "80"
  os: 'myvm'
  docker: dockerd

actions:
  - action: install
```

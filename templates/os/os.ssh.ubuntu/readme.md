#template: os.ssh.ubuntu

##Description:

This actor template allows the authorization of a certain key on a ubuntu machine , through the install action.
The actor can also return an executor instance to the specified machine, through the getExecutor action.

##Schema:
 - node: the node service  *Required*
 - sshkey: the pubkey to be added in the node machine
 - ssh.addr: addr of the node to connect to. *Required*
 - ssh.port: port the ssh service is running on the node. *Required*

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

```

# template: zerotier_daemon

## Description:

This actor template builds and installs the zerotier application on the specified os, and joins the specified network.
the network is specified in the helper service network.zerotier to allow 1 to many relationship.

## Schema:
 - os : type:string,  os service name to install on.
 - networks : type:list of strings, network.zerotier service nme to use.


## Example:
```yaml
sshkey__key1:

 node.physical__nodevm1:
   ip.public: 'ip'
   ssh.login: 'login'
   ssh.password: 'password'
   sshkey: 'key1'
   ssh.port: 22

os.ssh.ubuntu__osvm1:
  sshPort: 22
  sshkey: 'key1'
  node: 'nodevm1'

network.zerotier__gigstorage:
    id: '8056c2e21c000001'

zerotier_daemon__ztrvm1:
    os: 'osvm1'
    networks: ['gigstorage']
```
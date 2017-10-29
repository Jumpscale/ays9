# template: vfs

## Description

This actor template creates a file system on the specified node.

## Schema

- os: Parent os service, defined in the blueprint.

## Walkthrough

#@todo Better explanation of the function of the service
## Example

```yaml
sshkey__vfs_key:

node.physical__vfs_physical:
  ip.public: '172.17.0.2'
  ssh.login: 'root'
  ssh.password: '<root password>'
  ssh.addr: 'localhost'
  ssh.port: 22


os.ssh.ubuntu__vfs_os:
  sshAddr: 'localhost'
  sshPort: 22
  sshkey: 'vfs_key'
  node: 'vfs_physical'


vfs__main:
  os: 'vfs_os'
```

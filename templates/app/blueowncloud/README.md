# template: blueowncloud

## Description:
This actor is an umbrella service for creating a virtual machine with `Ubuntu 16.04 x64` image with a `btrfs` filesystem.

It creates
  - docker running `tidb` service instance.
  - docker running `owncloud` service instance (with *admin/admin* credentials).


## Schema:

- vdc: cloudspace to create the virtual machine on.
- **optional** ssh: sshkey used to manage the vm.
- datadisks: lists of disk sizes that will be attached to that vm.
-  hostprefix: the first part in your app url. (i.e hostprefix-machinedecimalip.gigapps.io )
-  fqdn = calculated by ays itself (i.e hostprefix-machinedecimalip.gigapps.io)
-  enablehttps = support for https. `default is False`


## Example blueprint

```yaml

g8client__env1:
    instance: '{ovc_config_instance(i.e. main)}'
    account: 'account'

vdc__myspaceb15:
    g8client: 'env1'
    location: 'be-conv-2'

blueowncloud__oc1:
    hostprefix: 'myapp'
    vdc: myspaceb15
    datadisks:
        - 1000
        - 1000

```

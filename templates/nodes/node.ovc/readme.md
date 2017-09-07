# template: node.ovc

## Description:
This actor template is responsible for creating a virtual machine on any openVCloud environment.

## Schema:

- description: arbitrary description of the vm. **optional**
- bootdisk.size: boot disk size in GB default:10.
- memory: memory available for the vm in GB. default:1.
- sizeID: will override memory parameter. Denotes type of VM, this size impact the number of CPU and memory available for the vm.
- os.image: OS image to use for the VM. default:'Ubuntu 15.10'.
- ports: List of port forwards to create. Format is `Public_port:VM_port` or `VM_port`.
if the public port is not specified, it will be chosen automatically in the available ports of the vdc.
e.g: to expose port 22 of the VM to the port 9000 on the public port of the vdc use :`9000:22`. **optional**
- machine.id: once the VM is created, holds the ID return by openvcloud for that VM. **filled in automatically, don't specify it in the blueprint**
- ip.public: public IP of the VM once installed. **filled in automatically, don't specify it in the blueprint**
- ip.private: private IP of the VM inside the VDC. **filled in automatically, don't specify it in the blueprint**
- ssh.login: login used to create ssh connection to the VM. **filled in automatically, don't specify it in the blueprint**
- ssh.password: password used to create ssh connection to the vm. **filled in automatically, don't specify it in the blueprint**
- vdc: service name of the vdc service where to deploy the VM. This is the parent service. If not specified, will try to use any defined in the blueprint. **required** to be defined in the blueprint
- ovf.link: the link to owncloud e.g http://mycloud.com/remote.php/webdav/ where you want to store the exported machine
- ovf.username: username for owncloud server
- ovf.password: password for owncloud server
- ovf.path: path to put the exported machine in e.g /exported_vms/machine.ovf
- ovf.callbackUrl: callbackurl for calling you back when the machine is exported
- disk: list of disk instances to be attached to the VM
- vmHistory: stores VM history which includes the actions performed on this machine and the time these actions were performed. **filled in automatically, don't specify it in the blueprint**
- uservdc: List of users to that access the machine with the type of access rights for each user e.g 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
- clone.name: The name of the machine that will be created when executing the clone action.
- snapshots: The list of snapshots of the node. **filled in when executing the listSnapshots action, don't specify it in the blueprint**
- snapshot.epoch: The epoch of a snapshot to rollback or delete.


### Changing port forwardings

 - Removing port forwarding in blueprints `section ports` will remove the portforwarding.
 - Adding new port forward in blueprint will add a new portforwarding.
 - Editing port forward in blueprint = removing the old portforward and creating new one.
 > port 22 is special case we keep it even if edited or deleted.

### Changing Disks

 - Removing disk from blueprint `disk` section will detach the disk from the machine.
 - Adding new disk in the blueprint will create a new disk and attach it to the machine, then set its IO limit.
 - Removing boot disks will be ignored.


## Example for creating machine
```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    description: 'vdc for demo'
    g8client: 'env'
    account: '<account>'
    location: '<location>'

disk.ovc__disk1:
  size: 5

# create the vm.
# expose ports 22. Map it to 2210.
node.ovc__demo:
    bootdisk.size: 50
    memory: 2
    os.image: 'Ubuntu 16.04 x64'
    ports:
        - '2210:22'
    disk:
      - 'disk1'

actions:
  - action: install
```

## Example for deleting machine
```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    location: '<location>'

node.ovc__demo:

actions:
  - action: uninstall
    actor: node.ovc
    service: demo
```

## Example for stopping machine
```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    location: '<location>'

node.ovc__demo:

actions:
  - action: stop
    actor: node.ovc
    service: demo
```

## Example for starting machine
```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    location: '<location>'

node.ovc__demo:

actions:
  - action: start
    actor: node.ovc
    service: demo
```

## Example for pausing machine
```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    location: '<location>'

node.ovc__demo:

actions:
  - action: pause
    actor: node.ovc
    service: demo
```

## Example for resuming machine
```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    location: '<location>'

node.ovc__demo:

actions:
  - action: resume
    actor: node.ovc
    service: demo
```

## Example for restarting machine
```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    location: '<location>'

node.ovc__demo:

actions:
  - action: restart
    actor: node.ovc
    service: demo
```

## Example for resetting machine
```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    location: '<location>'

node.ovc__demo:

actions:
  - action: reset
    actor: node.ovc
    service: demo
```

## Example for cloning machine

Executing the following blueprint will create a clone of the machine `demo` with name `demo_clone` in the same cloudspace.

```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    location: '<location>'

node.ovc__demo:
  cloneName: 'demo_clone'

actions:
  - action: clone
    actor: node.ovc
    service: demo
```

## Example for attaching new disks
If you need to attach disks to an already created machine you can execute a blueprint with the node adding to it all new disks.
The following example attaches a new disk `disk2` to the machine called `demo`.
```yaml
disk.ovc__disk2:
  size: 7

node.ovc__demo:
    disk:
      - 'disk1' # MUST be there to avoid detaching it
      - 'disk2'
```

## Example for detaching disks
If you need to detach disks from an already created machine you can execute a blueprint with the node removed from it the disks you need to detach:
The following example detaches `disk2` which was attached to node `demo` in the previous example, and leave `disk1` attached as it is.

```yaml
node.ovc__demo:
    disk:
      - 'disk1'
```

## Example for getting machine history
```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    location: '<location>'

node.ovc__demo:

actions:
  - action: get_history
    actor: node.ovc
```

## Example for attaching machine to external network
```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    location: '<location>'

node.ovc__demo:

actions:
  - action: attach_external_network
    actor: node.ovc
```

## Example for detaching machine from external network
```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    location: '<location>'

node.ovc__demo:

actions:
  - action: detach_external_network
    actor: node.ovc
```

## Example for adding user to a machine
```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    location: '<location>'

uservdc__demo_user:
    g8client: env

node.ovc__demo:
  uservdc:
    - name: demo_user
      accesstype: ACDRUX

actions:
  - action: add_user
    actor: node.ovc
    service: demo
```

## Example for updating user access right on a machine
```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    location: '<location>'

uservdc__demo_user:
    g8client: env

node.ovc__demo:
  uservdc:
    - name: demo_user
      accesstype: R

actions:
  - action: update_user
    actor: node.ovc
    service: demo
```

## Example for delete user access right from a machine
```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    location: '<location>'

uservdc__demo_user:
    g8client: env

node.ovc__demo:
  uservdc:
    - name: demo_user

actions:
  - action: delete_user
    actor: node.ovc
    service: demo
```

## Example for listing snapshots of a machine
```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    location: '<location>'

uservdc__demo_user:
    g8client: env

node.ovc__demo:

actions:
  - action: list_snapshots
    actor: node.ovc
    service: demo
```

## Example for taking snapshot of a machine
```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    location: '<location>'

uservdc__demo_user:
    g8client: env

node.ovc__demo:

actions:
  - action: snapshot
    actor: node.ovc
    service: demo
```

## Example for deleting snapshot of a machine
```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    location: '<location>'

uservdc__demo_user:
    g8client: env

node.ovc__demo:
  snapshotEpoch: <epoch of snapshot to be deleted>

actions:
  - action: delete_snapshot
    actor: node.ovc
    service: demo
```

## Example for rollbacking snapshot of a machine
```yaml
g8client__env:
    url: '<env_url>'
    login: '<login>'
    password: '<password>'
    account: '<account>'

vdc__vdcname:
    location: '<location>'

uservdc__demo_user:
    g8client: env

node.ovc__demo:
  snapshotEpoch: <epoch of snapshot to be rollbacked>

actions:
  - action: rollback_snapshot
    actor: node.ovc
    service: demo
```

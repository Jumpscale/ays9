# template: node.ovc

## Description:
This actor template is responsible to create a virtual machine on any openVCloud environment.

## Schema:

- description: arbitratry description of the vm. **optional**
- bootdisk.size: boot disk size in GB default:10.
- memory: memory available for the vm in GB. default:1.
- sizeID: will override memory parameter. Denotes type of VM, this size impact the number of CPU and memory available for the vm.
- os.image: OS image to use for the VM. default:'Ubuntu 15.10'.

- ports: List of port forward to create. Format is `Public_port:VM_port` or `VM_port`.
if the public port is not specified, it will be choose automaticlly in the available port of the vdc.
e.g: to expose port 22 of the VM to the port 9000 on the public port of the vdc use :`9000:22`. **optional**

- machine.id: once the VM is created, holds the ID return by openvcloud for that VM. **fill automaticlly, don't specify it in Blueprint**
- ip.public: public IP of the VM once installed. **fill automaticlly, don't specify it in Blueprint**
- ip.private: private IP of the VM inside the VDC. **fill automaticlly, don't specify it in Blueprint**

- ssh.login: login used to create ssh connection to the VM. **fill automaticlly, don't specify it in Blueprint**
- ssh.password: password used to create ssh connection to the vm. **fill automaticlly, don't specify it in Blueprint**

- vdc: service name of the vdc service where to deploy the VM. This is the parent service. If not specified, will try to use any defined in the blueprint. **required** to be defined in the blueprint

- ovf.link: the link to owncloud e.g http://mycloud.com/remote.php/webdav/ where you want to store the exported machine
- ovf.username: username for owncloud server
- ovf.password: password for owncloud server
- ovf.path: path to put the exported machine in e.g /exported_vms/machine.ovf
- ovf.callbackUrl: callbackurl for calling you back when the machine is exported
- disk: list of disk instances to be attached to the VM
- vmHistory: stores VM history which includes the actions performed on this machine and the time these actions were performed. **fill automatically, don't specify it in Blueprint**


### Changing port forwardings

 - Removing port forwarding in blueprints `section ports` will remove the portforwarding.
 - Adding new port forward in blueprint will add a new portforwardomg.
 - Editing port foward in blueprint = removing the old portforward and creating new one.
 > port 22 is special case we keep it even if edited or deleted.

### Changing Disks

 - Removing disk from blueprint `disk` section will detach the disk from the machine.
 - Adding new disk in the blueprint will create a new disk and attach it to the machine, then set its IO limit.
 - Removing boot disks will be ignored.


Replace \<with actual value \>

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

If you need to attach disks from an already created machine you can execute a blueprint with the node added to it all new disks
- The following example attaches a new disk `disk2` to the machine called `demo`
#### Example for attaching new disks
```yaml
disk.ovc__disk2:
  size: 7


node.ovc__demo:
    disk:
      - 'disk1' # MUST be there to avoid detaching it
      - 'disk2'
```

If you need to detach disks from an already created machine you can execute a blueprint with the node removed from it the disks you need to detach:
- The following example detaches `disk2` which was attached to node `demo` in the previous example, and leave `disk1` attached as it is
#### Example for detaching disks
```yaml
node.ovc__demo:
    disk:
      - 'disk1'
```
## Example for getting VM history
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

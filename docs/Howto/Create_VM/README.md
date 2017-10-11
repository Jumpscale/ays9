# How to Create a Virtual Machine

For creating a virtual machine use the **node.ovc** template, available here: https://github.com/Jumpscale/ays9/tree/master/templates/nodes/node.ovc

- [Minimal Blueprint](#minimal-blueprint)
- [Full Blueprint](#full-blueprint)
- [Values](#values)
- [Example](#example)
- [Using the AYS command line tool](#using-the-ays-command-line-tool)


<a id="minimal-blueprint"></a>
## Minimal Blueprint

```yaml
g8client__{environment}:
  url: '{url}'
  login: '{login}'
  password: '{password}'
  account: '{account}'

vdc__{vdc-name}:
  g8client: '{environment}'
  location: '{location}'

node.ovc__{vm-name}:
  vdc: "{vdc-name}"
  bootdiskSize: {bootdiskSize}
  memory: {memory}
  osImage: {osImage}

actions:
  - action: install    
```

<a id="full-blueprint"></a>
## Full blueprint

```yaml
g8client__{environment}:
  url: '{url}'
  login: '{login}'
  password: '{password}'
  account: '{account}'

vdcfarm__{vdcfarm}:

vdc__{vdc-name}:
  description: '{description}'
  vdcfarm: '{vdcfarm}'
  g8client: '{environment}'
  account: '{account}'
  location: '{location}'
  externalNetworkID: `{externalNetworkID}`

sshkey__{sshKey}:

node.ovc__{vm-name}:
  description: '{description}'
  vdc: '{vdc-name}'
  bootdiskSize: '{bootdiskSize}'
  memory:' {memory}'
  sizeID: {sizeID}
  osImage: '{image}'
  disk: '{disk}'
  sshkey: '{sshKey}'
  ovfLink: '{ovfLink}'
  ovfUsername: '{ovfUsername:}'
  ovfPassword: '{ovfPassword}'
  ovfPath: '{ovfPath}'
  ovfCallbackUrl: '{ovfCallbackUrl}'

actions:
  - action: install    
```

## Example

The below blueprint will create virtual machine (`myvm1`) with one data disk (`mydisk1`) of 500 GB that is limited to 2000 IOPS:

```yaml
g8client__cl:
  url: 'be-gen-1.demo.greenitglobe.com'
  login: '****'
  password: '****'
  account: '****'

vdc__vdctest1:
  g8client: 'cl'
  location: 'be-gen-1'

disk.ovc__mydisk1:
  type: "D"
  size: 500
  maxIOPS: 2000

node.ovc__myvm1:
  vdc: "myvdc"
  bootdisk.size: 20
  memory: 1
  os.image: 'Ubuntu 16.04 x64'
  disk:
    - mydisk1

actions:
  - action: install
```

## Values

- `{environment}`: OpenvCloud environment name for referencing elsewhere in the same blueprint or other blueprint in the repository
- `{url}`: URL to the environment, e.g. `gig.demo.greenitglobe.com`
- `{login}`: username on the OpenvCloud user
- `{password}`: password for the OpenvCloud user
- `{account}`: OpenvCloud account name
- `{vdc-name}`: name of the VDC that will be created, and if a VDC with the specified name already exists then that VDC will be used
- `{description}`: optional description for the virtual machine or VDC
- `{vdcfarm}`: optional name of the VDC farm to logically group VDCs; if not specified a new VDC farm will be created
- `{location}`: location where the VDC needs to be created
- `{bootdiskSize}`: size of the boot disk in GB, default is 10
- `{memory}`: memory available for the virtual machine in GB, default is 1

> Make sure to pass a value for `memory` that matches a VM size that supports the specified `bootdisksize`.
> Check the POST /cloudapi/sizes/list Cloud API for all available VM sizes for a given cloud space (values are in MB, so multiply `memory` with 1024)

- `{osImage}`: OS image to use for the virtual machine, default is 'Ubuntu 15.10'
- `{sizeID}`: specifies the number of virtual CPU cores, when specified you also override the value of `memory` since sizes are about the combination of the number of virtual CPU cores and memory
- `{ports}`: optional list of port forwards to create, formatted as `"public_port:VM_port"` or `"VM_port"`; if the public port is not specified, it will be choose automatically from the available VDC ports, e.g. in order to expose port 22 of the virtual machine to VDC port 9000 use `"9000:22"`
- `{disk}`: list of disk sizes in GB
- `{sshKey}`: SSH public key that get copied in `authorized_keys`
- `{ovfLink}`: link to webdav address where you to store the virtual machine When exported using the OVF format, e.g. `http://mycloud.com/remote.php/webdav/`
- `{ovfUsername:}`: username on the WebDAV server
- `{ovfPassword}`: password on the WebDAV server
- `{ovfPath}`: path to on the WebDAV server to put the OVF file, e.g. `/exported_vms/machine.ovf`
- `{ovfCallbackUrl}`: callback URL used when OVF export completed


## Using the AYS command line tool

You first will need to create a virtual datacenter, as documented in [How to create a VDC](../Create_VDC/README.md).

In case AYS is protected with ItsYou.online, you will first need to create a JWT, as documented in [How to Get a JWT](../Get_JWT/README.md).

Once you got your JWT, export the value:
```bash
export JWT='...'
```

Then execute the above blueprint and create a new run:
```bash
ays blueprint
ays run create
```

Optionally you can check the status of the run:
```bash
ays run list
ays run show -k <run-id>
```

Once the virtual machine got deployed, check the result using the `ays service` command:
```bash
ays service show -r node
```

This will show you all details of the ays service representing the actual virtual machine, including its instance data:
```bash
Instance data:
- bootdiskSize : 20
- ipPrivate : 192.168.103.254
- ipPublic : *****
- machineId : 737
- memory : 1
- osImage : Ubuntu 16.04 x64
- ports : ['2200:22']
- sizeID : -1
- sshLogin : cloudscalers
- sshPassword : *****
- sshPort : 2200
- stackID : -1
- vdc : myvdc
```

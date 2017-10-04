# Actions

[AYS services](../Definitions/Services.md) are controlled through their actions, which are implemented as Python functions in their `actions.py` files.

Each function corresponds to an action. In the example below the actor implements two actions, `install(job)` and `uninstall(job)`.

An action accepts a single argument called job.

The job object gives you access to multiple other useful objects:
- **job.service**: the service object on which the action is executed on
- **job.model.args**: the arguments passed to this action
- **job.service.model.data**: the schema values of the service

## Example

The below example is an `actions.py` for an OpenvCloud virtual machine:
- `install(job)` will create a new virtual machine
- `uninstall(job)` will delete the virtual machine

This AYS service has a parent-child relationship with an AYS service for a virtual data center.

```python
def install(job):
    service = job.service
    vdc = service.parent

    if 'g8client' not in vdc.producers:
        raise j.exceptions.AYSNotFound("no producer g8client found. cannot continue init of %s" % service)

    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)

    if service.name in space.machines:
        # machine already exists
        machine = space.machines[service.name]
    else:
        image_names = [i['name'] for i in space.images]
        if service.model.data.osImage not in image_names:
            raise j.exceptions.NotFound('Image %s not available for vdc %s' % (service.model.data.osImage, vdc.name))

        datadisks = list(service.model.data.datadisks)
        machine = space.machine_create(name=service.name,
                                       image=service.model.data.osImage,
                                       memsize=service.model.data.osSize,
                                       disksize=service.model.data.bootdiskSize,
                                       datadisks=datadisks)

    service.model.data.machineId = machine.id
    service.model.data.ipPublic = machine.space.model['publicipaddress']
    ip, vm_info = machine.get_machine_ip()
    service.model.data.ipPrivate = ip
    service.model.data.sshLogin = vm_info['accounts'][0]['login']
    service.model.data.sshPassword = vm_info['accounts'][0]['password']

    for i, port in enumerate(service.model.data.ports):
        ss = port.split(':')
        if len(ss) == 2:
            public_port, local_port = ss
        else:
            local_port = port
            public_port = None

        public, local = machine.create_portforwarding(publicport=public_port, localport=local_port, protocol='tcp')
        service.model.data.ports[i] = "%s:%s" % (public, local)

def uninstall(job):
    service = job.service
    vdc = service.parent

    if 'g8client' not in vdc.producers:
        raise j.exceptions.RuntimeError("no producer g8client found. cannot continue init of %s" % service)

    g8client = vdc.producers["g8client"][0]
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)
    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)

    if service.name not in space.machines:
        return
    machine = space.machines[service.name]
    machine.delete()
```

## Default actions

- `action_post_()`
- `action_pre_()`
- `check_down()`
- `check_requirements()`
- `check_up`
- `cleanup`
- `consume()`
- `data_export()`
- `data_import()`
- `delete()`
- `halt()`
- `init()`
- `input()`
- `init_actions_()`
- `monitor()`
- `processChange()`
- `removedata()`
- `start()`
- `stop()`


## Default behavior

Executing a blueprint with the delete action, as shown below, will automatically schedule excution of `service.delete()`. You can override this default behavior by implementing a custom `delete(job)` action.

```yaml
actions:
   - action delete
```

## HTTP request context

In some situations you may want to be able to access the http request context of a request within an action.

AYS allows you to access this context on the job object received in the service actions.

For example, if you want to access the JWT token used to create a run:
```python
# this is an snippet from a service action
def install(job):
    jwt_token = job.context['token']
    # ...
```

In the case you create a job from within another job, make sure you pass the context around:
```python
service.executeAction('start', context=job.context)
```

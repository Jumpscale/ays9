# Actions

[AYS services](Services.md) are controlled through their actions, which are implemented as Python functions in the `actions.py` files of their [actor](Actors.md). Each function corresponds to an action.

See [Actor Template Files](../ActorTemplateFiles/Actions.md) for an example of two actions: `install(job)` and `uninstall(job)`.

Actions are executed after they have been scheduled for execution.

Actions can get scheduled for execution in three ways:
- [As a result of executing a blueprint that includes an `actions:` section](#blueprint)
- [Because the action was scheduled for recurring execution as specified in the `config.yaml` of the actor template](#recurring)
- [Triggered by an AYS event for which the action was registered as an event handler](#events)

Each of them is discussed with an example here below.

<a id="blueprint"></a>
## Scheduling an execution with a blueprint

Executing the following blueprint will schedule to `install` action of the `myvdc` AYS service that was instantiated from a `vdc` actor:
```yaml
actions:
  - action: install
    actor: vdc
    service: myvdc
```

See [Blueprints](Blueprints.md) for more details.


<a id="recurring"></a>
## Recuring actions

Recurring actions are scheduled at the level of the actor template, meaning that all AYS services created from a specific version of an AYS actor will have them same recurring action configuration.

They are executed asynchronously with no [runs](Runs.md).

Here's an example of a `recurring` section in a `config.yaml`:
```yaml
recurring:
  - action: monitor
    period: 30s
    log: True

  - action: dosomethingelse
    period: 1m
    log: True
```

This configuration will result in AYS service with the `monitor()` action that is scheduled to be executed every 30 seconds, and a `dosomethingelse()` action scheduled for execution every minute.

See [Actor Configuration](../ActorTemplateFiles/Config.md) for more details about the `recurring` section.


<a id="events"></a>
## Actions handling events

Just as in the case of recurring actions, registering an action as an event handler for an AYS event is done through configuration at the level of the actor template, using an `events` section in the `config.yaml` of the template.

Here's an example of an `events` section in a `config.yaml`:

```yaml
events:
  - channel: telegram
    command: install_mynode
    actions:
      - install
      - actionX
    log: True
```

See [Actor Configuration](../ActorTemplateFiles/Config.md) for more details about the `events` section.

This configuration will schedule the actions `install()` and `actionX()` for execution every time the event `install_mynode` happens in the events channel `telegram`.

Note that actions can also be registered as event handlers at run time, using code. This and more details about events is covered in [Events](Events.md).


## Action states

States of an action:
- **new**: the action was never scheduled
- **scheduled**: the action is scheduled for execution
- **ok**: the action was executed successfully
- **error**: there was an error during execution


Checking the state of all actions of a specific AYS service is eays using the AYS command line tool:
```bash
cd /host/var/ays_repos/<repository-name>
ays service state -r <role of the AYS service> -n <name of the AYS service>
```

## Debug actions

See: [How to debug actor templates](../Howto/Debug_actor_templates/README.md).

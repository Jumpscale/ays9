# Actor Templates

In order to instantiate an AYS service you need an actor template.

Actor templates are definitions - or templates - for creating [Actors](Actors.md), based on which [AYS services](Services.md) are actually instantiated.

An AYS actor template defines:
- Relations to other AYS services on which the AYS service depends
- Application-specific attributes needed to instantiate the AYS service
- Which events triggered by other AYS services that need to be monitored and acted upon

An AYS actor template also implements [actions](Actions.md):
- Actions to install, start, stop and uninstall the actual application
- Actions to monitor the actual application, and how to act upon findings
- Actions to backup, restore, fail-over, auto-scale and keep the application healthy
- Actions to handle changes triggered by blueprints that update the application-spectic properties
- Any other application-specific action to manage the application

AYS actor templates can be local or global:
- **Global** actor templates are available to all AYS repositories from the AYS system directory `/opt/code/github/jumpscale/ays9`
- **Local** actor templates are only available to a specific AYS repository from its `actorTemplates` subdirectory

All this is defined and implemented in the [actor template files](../ActorTemplateFiles/README.md):

- [schema.capnp](../ActorTemplateFiles/Schema.md): describes all AYS service attributes that can be passed to AYS via a blueprint and/or set/changed by AYS   
- [config.yaml](../ActorTemplateFiles/Config.md): describes all relations (links), recurring actions, time outs, events and long running jobs of an AYS service
- [actions.py](../ActorTemplateFiles/Actions.md): implements all actions of the AYS service


## Roles

Both an actor template, actors and AYS service can be given a role, which is derived from the name of the AYS actor template.

For example for an AYS service based on the actor template with the name `node.ovc` the role is `node`.

So the role of an AYS service, actor or actor template is the first part of the actor template name before the `.` (dot).

In case there is no `.` (dot) in the name of the actor template, the role and actor template name are the same.

Multiple actor templates can have the same role, but a name needs to be unique. Roles are used to define categories of actors. For instance, `node.physical`, `node.docker` and `node.kvm` all serve the role `node`.

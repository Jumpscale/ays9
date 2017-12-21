# Actors

The actor of an AYS service is actually the combination of the following files in the `actors/<actor-name>` subdirectory of the AYS repository:
- `actions.py`: copy of the `actions.py` from the actor template
- `schema.capnp`: copy of the `schema.capnp` from the actor template
- `actor.json`: repository-specific metadata of all actions and events as defined in the actor template

As explained in [actor templates](ActorTemplates.md) actor templates are definitions - or templates - for creating actors, based on which [AYS services](Services.md) are actually instantiated.

The creation on an actor happens when the first AYS service of a specific actor template is instantiated in the AYS repository. All next AYS service instances in that repository that are based on this actor template are then using the same version of that actor template.

By having a local copy of the actor template in the `actors` directory of each actor template that is used in the AYS repository, AYS also allows to have different versions - and thus different behavior - of the AYS services per repository. And since an actor is part of the AYS repository you can keep track of the changes, again per repository.

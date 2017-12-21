# AYS Repositories

AYS repositories ("repos") are Git repositories containing [Blueprints](Blueprints.md), [AYS services](Services.md), [actors](Actors.md) and (optionally) local [actor templates](ActorTemplates.md).

On an AYS server the AYS repositories are always located in the `/opt/cockpit_repos` directory.

For each repository there will be a subdirectory:
```
/opt/cockpit_repos/repo1
/opt/cockpit_repos/repo2
...
```

And each AYS repository has the following 4 subdirectories:

- `/opt/cockpit_repos/<repository-name>/blueprints`

  - Contains the blueprints (YAML files) defining what needs to be done, see [Blueprints](Blueprints.md) for more details

- `/opt/cockpit_repos/<repository-name>/actorTemplates`

  - Local set of AYS actor templates, see [Actor Templates](ActorTemplates.md) for more details
  - AYS will always first look here for an AYS actor template, and if not found, will check the global actor templates, available from `/opt/code/github/jumpscale/ays9/templates`

- `/opt/cockpit_repos/<repository-name>/actors`

  - Here all the local copies of the AYS actor templates are stored, see [Actors](Actors.md) for more details
  - From the AYS actors one or more AYS service instances get created, all using the same version of the actor template
  - Has no further meaning than being a local copy, this is done to be able to see changes in the template on local (Git) repository level

- `/opt/cockpit_repos/<repository-name>/services`

  - Here the actual AYS services are residing, see [AYS Services](Services.md) for more details
  - `service.json`: which has checksums of all actions defined to track updated as well states and results of the executing actions and some metadata
  - `data.json`: has all the info as required to make a deployment reality (install)
  - `schema.capnp`: contains the service schema

# Life Cycle of an AYS Service Instance

The lifecycle of any service can be managed by AYS.

## Step 1: Create an AYS actor template

An AYS actor template defines:

```
- Relations between this service and other services. This is done through consumption.
- How to start/stop the service
- How to monitor the service
- How to backup/restore the service
- Any other relevant action which can be done on the AYS service
```

An AYS actor template is stored in an **AYS template repository** or locally in the `actorTemplates` directory of an **AYS repository**.

## Step 2: Create AYS blueprints using the AYS service

A service is typically deployed as part of a bigger solution, including other services, and that's where the AYS Blueprint is used for.

An AYS blueprint defines:

```
- Services that will be used or created
- Producers to be consumed (dependencies)
- Parent services to be consumed
- Attributes per service
```

## Step 3: AYS actor template gets "converted" into an AYS service recipe

An AYS service recipe is a copy of an AYS actor template, residing in a local AYS repository.

So an AYS actor template becomes an AYS service recipe when copied into the local AYS repository, where it will be used for actually deploying one or more instances of that service.

## Step 4: AYS service recipe gets "converted" into one or more AYS service instances

This happens when executing the `ays blueprint` command on the AYS repository.

What actually happens at that moment is that the data for each of the service instances gets created in `ays-repo/services/.../$servicerole!$serviceinstance/`.

The `data.json` has all the configuration settings for that AYS service instance. All the content of  `data.json` files get born out of the `schema.capnp` originating from the actor template which got "converted" to the service recipe.

## Step 5: Deploy & manage the AYS service instance

This starts when you actually install the AYS service instance.

The installation

```
- This can for instance be the provisioning of database content
- All types of actions now are possible on the AYS service instance
```

## Step 6: Update the version of a service

Imagine you have some service instances already deployed and a new version of that service is available. There can be multiple scenarios.

1. The new version only bring some change in the `actions.py` file, then you have to:

  - Download the new version of the template. Usually a simple `git pull` on the AYS templates repository is enough.
  - Execute the command `ays actor update`. Init action will walk over of the service recipe and update the `actions.py` file to the same version as the template of this service.

2. The new version bring new fields in the schema, then you have to:

  - Execute `ays actor update` 
  - Add these new field and their value to the blueprint.
  - execute `ays blueprint`. This command will walk over the blueprints and update the data accordingly. If there is some new fields they will be added to the `data.json`.


## Service deletion (service.delete(force=False))
Deleting services can cause problems and broken services state if not used with care, 

setting `force = True` in `service.delete` call
is a very damaging parameter, as It may delete its children or break a minimum required consumption of a consumer. 

setting `force = False` in `service.delete` will do a dryrun to see if you can delete services with no problems in the beginning. 

> it's always safer to use `force=False` and reason about your delete methods.

> service.delete triggers processChange with `links` changeCategory and producer_removed key containing the removed producer name and role.
### Default implementation for delete action
It uses `j.tools.async.wrappers.sync(job.service.delete())` meaning `force=False` for safe deletions by default.

```
!!!
title = "Service Lifecycle"
date = "2017-04-08"
tags = []
```

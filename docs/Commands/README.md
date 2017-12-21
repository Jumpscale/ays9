# AYS Commands

The commands available in the AYS command line tool is organized them into groups:  
 - actor
 - blueprint
 - repo
 - run
 - service
 - template
 - generatetoken

Each groups has sub-commands. To inspect the available sub-commands of a groups do `ays group --help`.

E.g.:
```shell
ays service --help
Usage: ays service [OPTIONS] COMMAND [ARGS]...

Group of commands about services

Options:
 --help  Show this message and exit.

Commands:
 delete  Delete a service and all its children Be...
 list    The list command lists all service instances...
 show    show information about a service
 state   Print the state of the selected services.
```

## Basic commands

The following commands show you the typical order in which you sends commands:
- [generate token](generatetoken.md) generates an ItsYou.online JWT token based on client_id and client_secret
- [repo create](repo/create.md) creates a new AYS repository
- [blueprint](blueprint/blueprint.md) executes one or more blueprints, converting them into AYS service instances
- [service show](service/show.md) inspects the AYS service that you created during the execution of the blueprint
- [run create](run/create.md) creates jobs (runs) for the scheduled actions, and proposes to start the jobs, which then executes the actions


## Complete list of all commands

- [actor](actor): group of actor commands
    - [list](actor/list.md): list all actors that exist in the current AYS repository
    - [update](actor/update.md): update an actor to a new version
- [blueprint](blueprint/blueprint.md): execute one or more blueprints, converting them into AYS service instances
- [generatetoken](generatetoken.md): generate an ItsYou.online JWT token based on client_id and client_secret
- [reload](reload.md): reload AYS objects in memory to include newly added objects
- [repo](repo): group of all AYS repositories commands
    - [create](repo/create.md): create a new AYS repository
    - [destroy](repo/destroy.md): reset all services & actors in current repository; (DANGEROUS) all AYS service instances will be lost!!!
    - [list](repo/list.md): list all known repositories
    - [delete](repo/delete.md): fully delete repository
- [run](run): group of run commands
    - [create](run/create.md): create jobs (runs) for the scheduled actions, and proposes to start the jobs, which then executes the actions
    - [list](run/list.md): list all the keys and creation date of the runs
    - [show](run/show.md): Print the details of a run
- [scheduler](scheduler): group of run scheduler commands
    - [status](scheduler/status.md): show information about the state of the run scheduler
- [service](service): group of AYS services commands
    - [delete](service/delete.md): delete an AYS service and all its children
    - [list](service/list.md): list all AYS services
    - [show](service/show.md): show information of an AYS service
    - [state](service/state.md): show state of all actions of an AYS service
- [start](start/start.md): start AYS server
- [template](template): group of all actor template commands
    - [list](template/list): list all available templates that can be used in a blueprint

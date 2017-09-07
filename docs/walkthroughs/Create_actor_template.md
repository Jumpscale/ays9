# Create an Actor Template

## Creating AYS repository

AYS repo contains service files and it is the environment in which a service instance is deployed and executed.

Use the command `ays repo create` to create the AYS repository, specifying the GitHub repository attached to it and the path where the repsitory will be created.

The command will create a directory containing the following:
- `actorTemplates`: This folder contains all your locally created templates and their files
- `blueprints`: Contains YAML files to define the nedded operations
- `services`: Contains services instances

An example command:
```bash
ays repo create -n {name} -g {github repo url}
```

## Creating an actor template
Actor templates defines the lifecycle of a service. It defines the service parameters and its interactions with other services as well as specifies the actions that need to be executed by each service.<br>

To create an actor {actor name}, you need to create a directory called {actor name} under <b>actorTemplates</b>. To allow configuration of your actor and establish the relationships between itself and other services, create `schema.capnp` and `config.yaml` files.
Parameter definition is as follows:
 - In the `schema.capnp` file:

    ```python
    @0xf3d30fa3ae2e10d8;
    struct Schema {
    	description @0 :Text;
    }
    ```

 - In the `config.yaml` file:
    ```yaml
    doc:
      property:
      - description: ''
    ```


There are two ways services can interact with each other:
- Consumption: A service instance can consume another service instance which is called a producer. A consumer is dependent on the producer and the producer need to be deployed before the consumer.
- Parenting: Is used to group services together by creating the child services as a subdirectory to the parent. The parent need to be created before the child unless the `optional` tag is used.

To establish a  producer/consumer relationship with another service:
- In the `schema.capnp` file:

   ```python
   @0xf3d30fa3ae2e10d8;
   struct Schema {
       node @0 :Text;
   }
   ```

- In the `config.yaml` file:
   ```yaml
   doc:
     property:
     - node: ''
   links:
     consume:
     - argname: node
       auto: false
       max: 1
       min: '0'
       role: node
   ```


Where relationship specifies the  minimum number of instances it can relate to. For example {min = 0, max = 1}
means that each service can consume between zero and one instance of the specified service.

Parent/children interaction:

- In the `schema.capnp` file:

   ```python
   @0xf3d30fa3ae2e10d8;
   struct Schema {
       node @0 :Text;
   }
   ```

- In the `config.yaml` file:
   ```yaml
   doc:
     property:
     - node: ''
   links:
     parent:
     - argname: node
       auto: false
       role: node
   ```

The relationship between parents and children is one to many.<br>

We can add these specifications to the interactions:

- The tag `auto` to create the specified service if it doesn't already exist in both interactions.

<i>actions.py</i> defines the behavior of the service. Each function in the python file corresponds to service action. The functions accept a single argument usually called job of type object. Using this object we can access the service object on which the actions is performed and the service parameters can be accessed.

The functions specified in the blueprints are executed when AYS is run. `install(job)` is usually the main function where the main operations of the service are implemented. In most cases it is the action that is expected to be executed when the AYS is run.

To use the parameters of the service inside the file use the job object as follows:
```
def install(job):
    service = job.service
    arga = service.model.data

```
To access the parameters of the parent and/or producer:
```
parent = service.parent.model.data
appDocker = service.producers['app_docker'][0]
```

## Blueprints

A blueprint is a YAML file that is used for interacting with AYS. It is responsible for specifying the deployment of a specific application. The required services instances are specified in this file and specifies their interactions. Blueprints are also used to indicate which actions should AYS execute.<br><br>
Create a [YAML](http://yaml.org/start.html) file inside the blueprints directory. The file specifies the instances that need to be created from every actor as well as the actions that need to be executed, for example the `install()` function.
```
node.packet.net__kvm:
    client: 'main'
    project.name: 'fake_project_name'
    plan.type: 'Type 0'
    device.os: 'Ubuntu 16.04 LTS'
    location: 'Parsippany'
    sshkey: 'main'
    actions:
        - action: install
```

In the above sample a new instance kvm is created. The client parameter references the instance of the service which is specified in <i>schema.capnp</i>. The actions field specifies the actions or functions to be executed by this instance.

## Running the services
To create the services and schedule the actions run the command `ays blueprint`. All files in the <b>blueprints</b> directory will be used for the creation of the instances.<br>

The command `ays run create` execute the functions specified in the blueprints files. It searches for all scheduled, error or changed actions and start a run to execute these actions.<br>

`ays repo destroy` deletes all services instances as well as all scheduled actions in the repo.

To reload the blueprint files, first use `ays repo destroy` followed by `ays blueprint`

```
!!!
title = "Ays Walkthrough"
date = "2017-04-08"
tags = []
```

# Create a JS9 Docker Container

In order to have your own AYS server creating a JumpScale9 Docker container is the easiest and quickest way, just follow the instructions in the [jumpscale/developer](https://github.com/Jumpscale/developer) repository.

Below is an example based on these instructions.

Optionally first check if there is already JS9 Docker container running:
```shell
docker ps -a
```

If there is one running, stop and remove it:
```shell
docker stop <CONTAINER ID>
docker rm <CONTAINER ID>
```

And also check and remove all images:
```shell
docker images
docker rmi <IMAGE ID>
```

Then check, if your private SSH key is loaded by ssh-agent:
```shell
ssh-add -l
```

If not loaded, execute:
```shell
eval "$(ssh-agent -s)"
ssh-add -K ~/.ssh/id_rsa
```

Set the directory where the container volumes should be mounted on the machine hosting the Docker container:
```shell
export GIGDIR="/home/$USER/gig9" #on MacOS: export GIGDIR="/Users/$USER/gig9"
rm -rf $GIGDIR
```

Set the branch of JumpScale to be installed in the Docker container:
```shell
export GIGBRANCH="master"
```

Set the branch of the developer repository to be used:
```shell
export GIGDEVELOPERBRANCH="master"
```

Get and execute `jsinit.sh` in order to prepare for the actual work:
```shell
rm -rf /tmp/jsinit.sh
curl "https://raw.githubusercontent.com/Jumpscale/developer/${GIGDEVELOPERBRANCH}/jsinit.sh?$RANDOM" > /tmp/jsinit.sh
bash /tmp/jsinit.sh
```

Use `jsenv.sh` to source your environment:
```shell
source ~/.jsenv.sh
```

> Remember to always execute `source ~/.jsenv.sh` prior to executing for the first time (e.g. in a new terminal session) any of the `js9_` commands.

And finally, start the actual building of your image with the `js9_build ` script:
```shell
js9_build -p
```

Now to start the container:
```shell
js9_start
```

In order to SSH into your `js9` container:
```shell
ssh -A root@localhost -p 2222
```

For more details on the JumpScale9 Docker container see https://github.com/Jumpscale/developer.

Next you will probably want start the AYS service, as documented in [Start AYS](startays.md).

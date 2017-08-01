# Create a JS9 Docker Container

In order to have your own AYS server instance creating a JumpScale9 Docker container is the easiest and quickest way, just follow the below steps.

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



And finally, start the actual building of your image with the `js9_build ` script, which will also start your container with the name `js9_base`:
```shell
source ~/.jsenv.sh
js9_build -l -p
```

Now to start the container:
```shell
js9_start
```

> Remember to always execute `source ~/.jsenv.sh` prior to executing for the first time (e.g. in a new terminal session) any of the `js9_` commands.

In order to SSH into your `js9` container:
```shell
ssh -A root@localhost -p 2222
```

For more details on the JumpScale9 Docker container see https://github.com/Jumpscale/developer.

Next you will probably want start the AYS service, as documented in [Start AYS](startays.md).


#TODO: *1 needs to be done
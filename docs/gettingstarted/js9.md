# Create a JS9 Docker Container

In order to have your own AYS server creating a JumpScale9 Docker container is the easiest and quickest way, just follow the instructions in the [jumpscale/bash](https://github.com/Jumpscale/bash) repository.

Installing the master branch of the Bash tools (Z-tools):
```bash
export ZUTILSBRANCH="master"
export ZBRANCH="master"
curl https://raw.githubusercontent.com/Jumpscale/bash/${ZUTILSBRANCH}/install.sh?$RANDOM > /tmp/install.sh;bash /tmp/install.sh
```

Make the bash tools available:
```bash
source ~/.bash_profile
```

Then go for the option to create a Docker container with core + lib + prefab + ays + portal:
```bash
ZInstall_portal9
```

Check the Docker images:
```bash
docker images
```

Check the Docker containers:
```bash
docker images
```

Start the container:
```bash
ZDockerActive -b jumpscale/<imagename> -i <name of your docker>
```


For more details on the JumpScale9 Docker container see https://github.com/Jumpscale/bash.

Next you will probably want start the AYS service, as documented in [Start AYS](startays.md).
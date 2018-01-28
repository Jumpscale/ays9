# Deploy Zero-OS on Packet.net

## Start an AYS service

 To start the AYS service, use the `ays start` command.

```bash
Usage: ays start [OPTIONS]

start an ays service in tmux

Options:
  -b, --bind TEXT     listening address
  -p, --port INTEGER  listening port
  --debug             enable debug logging
  --help              Show this message and exit.
```

Example:
`ays start --bind 0.0.0.0 --port 8080 --debug`

## Execute blueprint to deploy Zero-OS on Packet.net

Create a new repository starting from an existing one:
```bash
ays repo create -n myrepo -g ssh://git@docs.greenitglobe.com:10022/despiegk/cockpit_g8os_testenv.git
```

Get an exinsting blueprint:
```bash
cd /host/var/ays_repos/myrepo/blueprints
rm -f 1_server.yaml
wget https://raw.githubusercontent.com/g8os/ays_template_g8os/master/examples/ays_g8os_packetnet/blueprints/1_server.yaml
```

Execute the blueprint in order to initialize the AYS service:
```bash
cd ..
ays blueprint 1_server.yaml
```

Start a run so that all scheduled actions are executed:
```bash
ays run create --follow
```

## Check the logs

```
ays run show -l
```

## Check the service info of your AYS service

Shows service info from all services with role node:
```
ays service show --role node
```

## Update all your actors in the repo

This will make sure that active AYS services use the most recent actor version

```bash
cd /host/var/ays_repos/myrepo
ays actor update
```

## Remove all AYS services

```
ays service delete
```

This will ask which services to remove.

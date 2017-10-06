# AYS Server Configuration

AYS is configured through a simple configuration file: `/etc/jumpscale9.toml`:
```toml
[ays]
production = false

[ays.oauth]
jwt_key = ""
organization = ""

[dirs]
BASEDIR = "/opt"
BASEDIRJS = "/opt/jumpscale9"
BINDIR = "/opt/bin"
BUILDDIR = "/host/var/build"
CFGDIR = "/opt/cfg"
CODEDIR = "/opt/code"
DATADIR = "/host/var/data"
HOMEDIR = "/root"
HOSTCFGDIR = "/hostcfg"
HOSTDIR = "/host"
JSAPPSDIR = "/opt/jumpscale9/app"
LIBDIR = "/opt/lib/"
LOGDIR = "/host/var/log"
TEMPLATEDIR = "/host/var/templates"
TMPDIR = "/tmp"
VARDIR = "/host/var"


[email]
from = "info@incubaid.com"
smtp_port = 443
smtp_server = ""

[git]

[git.ays]
branch = "master"
url = "https://github.com/Jumpscale/ays9.git"

[git.js]
branch = "master"
url = "https://github.com/Jumpscale/core9.git"

[grid]
gid = 0
nid = 0

[me]
fullname = ""
loginname = ""

[plugins]
JumpScale9 = "/opt/code/github/jumpscale/core9/JumpScale9"
JumpScale9AYS = "/opt/code/github/jumpscale/ays9/JumpScale9AYS"
JumpScale9Lib = "/opt/code/github/jumpscale/lib9/JumpScale9Lib"
JumpScale9Portal = "/opt/code/github/jumpscale/portal9/JumpScale9Portal"
JumpScale9Prefab = "/opt/code/github/jumpscale/prefab9/JumpScale9Prefab"

[redis]
addr = "localhost"
port = 6379

[ssh]
SSHKEYNAME = "id_rsa"

[system]
autopip = false
container = true
debug = false
readonly = false
```

AYS uses Redis to store its data, two modes are supported: `TCP` and `Unix socket`, `TCP` is the default.

If no Redis configuration is provided the default behavior is to try to connect over a Unix socket located at `/tmp/redis.sock`:
```toml
[redis]
unixsocket = "/tmp/redis.sock"
```

## Redis server configuration

By default Redis is an in-memory only key-value store. But for our use case we want the data to be persisted on disk even after the server has stopped. To do that, we need to configure the Redis server to save its data on disk.

Here is an example of valid Redis configuration for AYS:
```
# disable listening on tcp socket
port 0

# specify location of the unixsocket
unixsocket /tmp/ays.sock

# change location where to dump the database files
dir /optvar/data/redis-server

# By default Redis asynchronously dumps the dataset on disk. This mode is
# good enough in many applications, but an issue with the Redis process or
# a power outage may result into a few minutes of writes lost (depending on
# the configured save points).
#
# The Append Only File is an alternative persistence mode that provides
# much better durability. For instance using the default data fsync policy
# (see later in the config file) Redis can lose just one second of writes in a
# dramatic event like a server power outage, or a single write if something
# wrong with the Redis process itself happens, but the operating system is
# still running correctly.
#
# AOF and RDB persistence can be enabled at the same time without problems.
# If the AOF is enabled on startup Redis will load the AOF, that is the file
# with the better durability guarantees.
#
# Please check http://redis.io/topics/persistence for more information.
appendonly yes
```

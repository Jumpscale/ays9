#!/bin/bash
set -e
set -x

export SSHKEYNAME=id_rsa

if [ -n $TRAVIS_EVENT_TYPE ] && [ $TRAVIS_EVENT_TYPE == "cron" ]; then
    # Start ays9 container
    sudo -HE bash -c "source /opt/code/github/jumpscale/bash/zlibs.sh; ZKeysLoad; ZDockerActive -b jumpscale/ays9 -i ays9"    
    # Install capnp tools if not exist
    if [ ! `which capnp` ]; then 
        sudo -HE bash -c "ssh -tA  root@localhost -p 2222 \"cd /tmp/;curl -O https://capnproto.org/capnproto-c++-0.6.1.tar.gz;tar zxf capnproto-c++-0.6.1.tar.gz;cd capnproto-c++-0.6.1;./configure;make install\""
    fi
    # Install RQ
    sudo -HE bash -c "ssh -tA root@localhost -p 2222 \"pip install rq\""
else
    # Start ays9 container
    sudo -HE bash -c "source /opt/code/github/jumpscale/bash/zlibs.sh; ZKeysLoad; ZDockerActive -b jumpscale/ays9nightly -i ays9"
    sudo -HE bash -c "source /opt/code/github/jumpscale/bash/zlibs.sh; ZKeysLoad; container 'pip install -e /opt/code/github/jumpscale/core9'"
    sudo -HE bash -c "source /opt/code/github/jumpscale/bash/zlibs.sh; ZKeysLoad; container 'pip install -e /opt/code/github/jumpscale/lib9'"
    sudo -HE bash -c "source /opt/code/github/jumpscale/bash/zlibs.sh; ZKeysLoad; container 'pip install -e /opt/code/github/jumpscale/prefab9'"
    sudo -HE bash -c "source /opt/code/github/jumpscale/bash/zlibs.sh; ZKeysLoad; container 'pip install -e /opt/code/github/jumpscale/ays9'"
fi

# Dump the environment variables as json file in a the container cfg dir
sudo -HE bash -c "python -c 'import json, os;print(json.dumps({\"BACKEND_ENV\": dict([(key, value) for key, value in os.environ.items() if key.startswith(\"BACKEND_\")])}))' > ~/js9host/cfg/ays_testrunner.json"

# Run tests
sudo -HE bash -c "ssh -tA  root@localhost -p 2222 \"cd /opt/code/github/jumpscale/ays9; /bin/bash test.sh $TRAVIS_EVENT_TYPE\""

if [ -n $TRAVIS_EVENT_TYPE ] && [ $TRAVIS_EVENT_TYPE == "cron" ]; then
    sudo -HE bash -c "source /opt/code/github/jumpscale/bash/zlibs.sh; ZKeysLoad; ZDockerCommit -b jumpscale/ays9 -i ays9"
else
    sudo -HE bash -c "source /opt/code/github/jumpscale/bash/zlibs.sh; ZKeysLoad; ZDockerCommit -b jumpscale/ays9nightly -i ays9"
fi

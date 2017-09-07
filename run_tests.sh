#!/bin/bash
eval $(ssh-agent)
ssh-add

# Start ays9 container
sudo -HE bash -c "source /opt/code/github/jumpscale/bash/zlibs.sh; ZDockerActive -b jumpscale/ays9 -i ays9"

# Install capnp tools
sudo -HE bash -c "ssh -tA  root@localhost -p 2222 \"cd /tmp/;curl -O https://capnproto.org/capnproto-c++-0.6.1.tar.gz;tar zxf capnproto-c++-0.6.1.tar.gz;cd capnproto-c++-0.6.1;./configure;make install\""

# Install RQ
sudo -HE bash -c "ssh -tA root@localhost -p 2222 \"pip install rq\""

# Run core tests
sudo -HE bash -c "ssh -tA  root@localhost -p 2222 \"cd /opt/code/github/jumpscale/ays9; /bin/bash test.sh\""

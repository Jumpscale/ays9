#!/bin/bash
set -e

# Install ays9 in a docker contianer using bash installers
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa

export ZUTILSBRANCH=${ZUTILSBRANCH:-master}

curl https://raw.githubusercontent.com/Jumpscale/bash/$ZUTILSBRANCH/install.sh?$RANDOM > /tmp/install.sh;sudo -E bash /tmp/install.sh
sudo -HE bash -c "source /opt/code/github/jumpscale/bash/zlibs.sh; ZCodeGetJS"
sudo -HE bash -c "source /opt/code/github/jumpscale/bash/zlibs.sh; ZDockerInstallLocal"
eval $(ssh-agent)
ssh-add
sudo -HE bash -c "source /opt/code/github/jumpscale/bash/zlibs.sh; ZInstall_ays9"

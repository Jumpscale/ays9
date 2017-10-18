#!/bin/bash

# uploads the successfully built js9 ays image to dockr hub for development re-use

export SSHKEYNAME=id_rsa

if [ -n $TRAVIS_EVENT_TYPE ] && [ $TRAVIS_EVENT_TYPE == "cron" ]; then
    sudo -HE bash -c "source /opt/code/github/jumpscale/bash/zlibs.sh; ZKeysLoad; ZDockerCommit -b jumpscale/ays9 -i ays9"
    image_id=$(sudo docker images -q jumpscale/ays9)
    sudo docker tag $image_id jumpscale/ays9nightly:latest
    sudo docker login -u ${DOCKERHUB_LOGIN} -p ${DOCKERHUB_PASS}
    sudo docker push jumpscale/ays9nightly
fi

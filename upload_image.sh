#!/bin/bash

# uploads the successfully built js9 ays image to dockr hub for development re-use

sudo docker login -u ${DOCKERHUB_LOGIN} -p ${DOCKERHUB_PASS}
sudo docker push jumpscale/ays9

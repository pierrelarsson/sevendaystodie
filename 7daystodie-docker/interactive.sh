#!/bin/bash

sudo docker run --rm --interactive --tty \
    --net host \
    --name 7daystodie \
    --volume /srv/7daystodie:/srv/7daystodie \
    7daystodie-docker:latest-pierre

#    7daystodie-docker:latest-pierre -beta public

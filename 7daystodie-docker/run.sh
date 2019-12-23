#!/bin/bash

sudo docker run --detach --interactive --tty \
    --net host \
    --restart always \
    --name 7daystodie \
    --volume /srv/7daystodie:/srv/7daystodie \
    7daystodie-docker:latest-pierre

sudo docker attach --detach-keys 'ctrl-d' 7daystodie

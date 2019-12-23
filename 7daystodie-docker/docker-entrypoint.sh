#!/bin/bash

umask 0002
mkdir --verbose --parents ./Steam
rm --verbose --force ./Steam/appcache/appinfo.vdf

if [ ! -e ./Steam/linux32/steamcmd ]; then
    curl --location "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" | tar \
        --verbose \
        --gzip \
        --extract \
        --directory=./Steam \
        --file=-
fi

./Steam/linux32/steamcmd \
    +login anonymous \
    +force_install_dir $PWD \
    +app_update 294420 "$@" \
    +quit

ulimit -c 0

exec ./7DaysToDieServer.x86_64 \
    -quit \
    -batchmode \
    -nographics \
    -dedicated \
    -configfile=./serverconfig.xml

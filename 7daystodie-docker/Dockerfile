FROM centos:7

RUN yum --assumeyes update glibc libstdc++ \
    && yum --assumeyes install glibc.i686 libstdc++.i686 \
    && yum clean all

COPY docker-entrypoint.sh /

RUN install --verbose --mode=0777 --directory /srv/7daystodie \
    && chmod --verbose 0755 /docker-entrypoint.sh

VOLUME ["/srv/7daystodie"]

USER 65534:65534

WORKDIR /srv/7daystodie

ENV HOME=/srv/7daystodie \
    LD_LIBRARY_PATH=/srv/7daystodie/Steam/linux64:/srv/7daystodie/Steam/linux32:/srv/7daystodie/7DaysToDieServer_Data/Plugins/x86_64:/srv/7daystodie

ENTRYPOINT ["/docker-entrypoint.sh"]

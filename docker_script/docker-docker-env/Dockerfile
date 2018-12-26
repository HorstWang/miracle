FROM ubuntu:16.04
MAINTAINER horst.wang@emc.com

RUN apt-get update
COPY ./init-docker.sh ./init-docker.sh
RUN ./init-docker.sh
ENTRYPOINT c=1; while [ $c -lt 5 ]; do sleep 1; echo .; done

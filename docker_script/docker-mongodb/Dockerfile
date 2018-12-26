FROM ubuntu:18.04
MAINTAINER horst.wang@emc.com

RUN apt-get update --allow-unauthenticated
RUN apt-get install gnupg2 -y
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4
RUN apt-get install lsb-core -y
RUN echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-4.0.list
RUN apt-get update --allow-unauthenticated
RUN export DEBIAN_FRONTEND=noninteractive && apt-get install -y mongodb-org && echo "mongodb-org hold" | dpkg --set-selections && echo "mongodb-org-server hold" | dpkg --set-selections && echo "mongodb-org-shell hold" | dpkg --set-selections && echo "mongodb-org-mongos hold" | dpkg --set-selections && echo "mongodb-org-tools hold" | dpkg --set-selections
ENTRYPOINT mongod --config /my/custom/mongod.conf

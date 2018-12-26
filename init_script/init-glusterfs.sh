#/bin/bash

sudo apt-get -y install software-properties-common
sudo add-apt-repository -y ppa:gluster/glusterfs-3.10
sudo apt-get -y update
sudo apt-get -y install glusterfs-server
sudo update-rc.d glusterfs-server defaults

#/bin/bash

sudo docker images -a
sudo docker rmi $(sudo docker images -a -q) -f > /dev/null 2>&1
sudo docker images -a

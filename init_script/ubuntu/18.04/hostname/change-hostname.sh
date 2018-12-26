#/bin/bash

sudo sed -i 's/preserve_hostname:\s*\S*\s*$/preserve_hostname: true/' /etc/cloud/cloud.cfg
sudo hostnamectl set-hostname $1 --static

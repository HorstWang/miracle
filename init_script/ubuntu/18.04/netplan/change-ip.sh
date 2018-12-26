#/bin/bash

IP=$1
GATEWAY=$2
if [ "$IP" = "" ]
then
  echo 'Must specify a valid IP address.'
  exit
fi
if [ "$GATEWAY" = "" ]
then
  echo 'Must specify a valid gateway address.'
  exit
fi

sudo rm -rf /etc/netplan/*
sudo cp ./50-cloud-init.yaml /etc/netplan/
sudo sed -i 's/#addresses: \[.*\]/addresses: ['$IP'\/24]/' /etc/netplan/50-cloud-init.yaml
sudo sed -i 's/#gateway4: \S\+/gateway4: '$GATEWAY'/' /etc/netplan/50-cloud-init.yaml
sudo sed -i 's/#dhcp4: \S\+/dhcp4: no/' /etc/netplan/50-cloud-init.yaml
sudo sed -i 's/#nameservers:/nameservers:\n                addresses: ['$GATEWAY',8.8.8.8]/' /etc/netplan/50-cloud-init.yaml

sudo netplan apply

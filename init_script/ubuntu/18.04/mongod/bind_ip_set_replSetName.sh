#/bin/bash

config=/etc/mongod.conf

hs_name=$(hostname)
rs_name=rs0
port=27017
KEYPATH=$(echo $HOME | sed -r 's/\//\\\//g')

if [ \( "$1" = 'shard' \) -o \( "$1" = 'config' \) ]
then
  sudo sed -i 's/#sharding:/sharding:\n  clusterRole: '$1'svr/' $config
  rs_name=$rs_name-$1
fi

if [ "$1" = 'shard' ]
then
  port=27018
elif [ "$1" = 'config' ]
then
  port=27019
fi

sudo sed -i 's/port:.*$/port: '$port'/' $config
sudo sed -i 's/bindIp:.*$/bindIp: 127.0.0.1,'$hs_name'/' $config
sudo sed -i 's/#replication:/replication:\n  replSetName: "'$rs_name'"/' $config
if [ \( "$1" = 'shard' \) -o \( "$1" = 'config' \) ]
then
  sudo sed -i 's/#security:/security:\n  keyFile: '$KEYPATH'\/keyfile.key/' $config
fi

sudo systemctl restart mongod
sudo systemctl status mongod | cat

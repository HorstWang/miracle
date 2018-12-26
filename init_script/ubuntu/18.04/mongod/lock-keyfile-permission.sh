#/bin/bash

keyfile=$HOME/keyfile.key
sudo chown mongodb:users $keyfile
sudo chmod 400 $keyfile

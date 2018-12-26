#/bin/bash

TAG=$1

./inifuc.sh purge
./inifuc.sh build $TAG
./inifuc.sh push $TAG
./inifuc.sh purge

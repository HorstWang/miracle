#/bin/bash

TAG=$1

echo '----------PURGE----------'
./inifuc_jenkins.sh purge
echo '----------BUILD----------'
./inifuc_jenkins.sh build $TAG
echo '----------PUSH----------'
./inifuc_jenkins.sh push $TAG
echo '----------PURGE----------'
./inifuc_jenkins.sh purge

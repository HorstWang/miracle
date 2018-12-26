#/bin/bash

echo '----------BEFORE killing containers----------'
docker ps -a
CONTAINER_IDS=$(docker ps -a | grep 'vplex_log_server\|vplex_log_parser\|vplex_log_db' | awk '{ print $1 }')
docker stop $CONTAINER_IDS > /dev/null 2>&1
docker rm $CONTAINER_IDS > /dev/null 2>&1
echo '----------AFTER killing containers----------'
docker ps -a

#/bin/bash

echo '----------BEFORE removing images----------'
docker images -a
docker rmi $(docker images | grep 'vplex_log_db\|vplex_log_parser\|vplex_log_server' | awk '{ print $3 }') -f > /dev/null 2>&1
echo '----------AFTER removing images----------'
docker images -a

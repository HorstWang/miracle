#/usr/bin/bash

apt-get update -y
echo '--------------Install missing tools--------------'
echo '--------------curl--------------'
apt-get install curl -y
echo '--------------software-properties-common--------------'
apt-get install --reinstall software-properties-common -y
echo '--------------lsb-release--------------'
apt-get install lsb-release -y
echo '--------------apt-transport-https--------------'
apt-get install apt-transport-https
echo '--------------curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - --------------'
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
echo '--------------add-apt-repository--------------'
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt-get update -y
echo '--------------apt-cache policy docker-ce--------------'
apt-cache policy docker-ce
echo '--------------apt-get install -y docker-ce--------------'
apt-get install -y docker-ce
echo '--------------Complete installing docker-ce--------------'
#systemctl status docker
echo 'DOCKER_OPTS="--iptables=false"' | tee -a /etc/default/docker
service docker restart

echo 'systemctl status docker'
systemctl status docker | cat
#echo 'Run the following command to check docker service status.'
#echo 'systemctl status docker'

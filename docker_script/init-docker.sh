#/usr/bin/bash

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update -y
apt-cache policy docker-ce
sudo apt-get install -y docker-ce
#sudo systemctl status docker
echo 'DOCKER_OPTS="--iptables=false"' | sudo tee -a /etc/default/docker
sudo service docker restart

echo 'Run the following command to check docker service status.'
echo 'sudo systemctl status docker'

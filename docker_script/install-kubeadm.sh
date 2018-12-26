#/bin/bash

sudo apt-get update && sudo apt-get install -y apt curl
wget http://packages.cloud.google.com/apt/doc/apt-key.gpg --no-check-certificate && cat ./apt-key.gpg | sudo apt-key add -
sudo /bin/bash -c "cat <<EOF >/etc/apt/sources.list.d/kubernetes.list
deb http://apt.kubernetes.io/ kubernetes-xenial main
EOF"
sudo cp ./disable-apt-ssl /etc/apt/apt.conf.d/
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

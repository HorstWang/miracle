#/bin/bash

KUBE_VER=1.12.1-00

sudo apt-get update && sudo apt-get install -y apt curl
wget http://packages.cloud.google.com/apt/doc/apt-key.gpg --no-check-certificate && cat ./apt-key.gpg | sudo apt-key add -
sudo /bin/bash -c "cat <<EOF >/etc/apt/sources.list.d/kubernetes.list
deb http://apt.kubernetes.io/ kubernetes-xenial main
EOF"
sudo cp ./disable-apt-ssl /etc/apt/apt.conf.d/
sudo apt-get update
sudo apt-get install -y kubelet=$KUBE_VER kubeadm=$KUBE_VER kubectl=$KUBE_VER --allow-change-held-packages
sudo apt-mark hold kubelet kubeadm kubectl

echo 'Disable swap to avoid issue "Swap not supported"'
sudo swapoff -a

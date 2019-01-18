#/bin/bash

pip_proxy_param=

if [[ ! "$http_proxy" == "" ]]
then
    pip_proxy_param=--proxy=$http_proxy
fi

sudo apt-get update -y
sudo apt-get install zlib1g-dev -y
sudo apt-get install libssl-dev -y
sudo apt-get install openssl -y
sudo apt-get install build-essential -y
sudo apt-get install libsqlite3-dev -y
sudo apt-get install libsm6 libxrender1 libfontconfig1 -y
sudo apt-get install mysql-server -y
sudo apt-get install libmysqlclient-dev -y
wget https://www.python.org/ftp/python/3.6.2/Python-3.6.2.tar.xz
tar -xvf ./Python-3.6.2.tar.xz
cd ./Python-3.6.2
./configure --prefix=/opt/Python-3.6.2 --enable-loadable-sqlite-extensions
make
sudo make install
cd /opt/Python-3.6.2/bin/
sudo ./pip3.6 install virtualenv $pip_proxy_param
cd ~
/opt/Python-3.6.2/bin/virtualenv venv_py_3.6.2 -p /opt/Python-3.6.2/bin/python3.6
source ./venv_py_3.6.2/bin/activate
pip install ipython $pip_proxy_param
pip install pandas $pip_proxy_param
pip install mysqlclient $pip_proxy_param
pip install django $pip_proxy_param
pip install xlwt $pip_proxy_param
#sudo apt-get install ubuntu-desktop -y
#sudo apt-get install mysql-workbench -y
#sudo shutdown -r now

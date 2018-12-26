Initial software environment
cd ./init_script
sudo /bin/bash ./init-django.sh
sudo /bin/bash ./init-python2.sh
sudo /bin/bash ./init-logtool.sh
cat ./init-database.sh | mysql -u root -p
cd ../docker_script/
sudo /bin/bash ./init-docker.sh
sudo /bin/bash ./init-docker-compose.sh
sudo mkdir /log_download
sudo chown -R wangh11:root /log_download/

If execute in docker on multi nodes:
1. Setup glusterfs and mount with /log_download;
2. sudo mkdir /log_download/mysql;

Initial database table
source ~/venv_py_3.6.2/bin/activate
cd kattegat/
source ./env_var
python manage.py migrate
cd ~/kattegat/kattegat/vplex/err_code_xml
python ./err_code_xml_parser.py -f ./VPlexErrCode.bin.Debug.50.xml -v 5.0
python ./err_code_xml_parser.py -f ./VPlexErrCode.bin.Debug.51.xml -v 5.1
python ./err_code_xml_parser.py -f ./VPlexErrCode.bin.Debug.52.xml -v 5.2
python ./err_code_xml_parser.py -f ./VPlexErrCode.bin.Debug.53.xml -v 5.3
python ./err_code_xml_parser.py -f ./VPlexErrCode.bin.Debug.54.xml -v 5.4
python ./err_code_xml_parser.py -f ./VPlexErrCode.bin.Debug.55.xml -v 5.5
python ./err_code_xml_parser.py -f ./VPlexErrCode.bin.Debug.60.xml -v 6.0

Debug commands
Start rolling log extraction job command: sudo /bin/bash -c 'export DB_CONTAINER_NAME=localhost && cd /log_download && python /LogAnalysis/rolling_job.py'

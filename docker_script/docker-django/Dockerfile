FROM ubuntu:16.04
MAINTAINER horst.wang@emc.com

RUN apt-get update
RUN apt-get install zlib1g-dev -y
RUN apt-get install libssl-dev -y
RUN apt-get install openssl -y
RUN apt-get install build-essential -y
RUN apt-get install libsqlite3-dev -y
RUN apt-get -y install libsm6 libxrender1 libfontconfig1 -y
RUN apt-get -y install nmap
RUN apt-get -y install libmysqlclient-dev
RUN apt-get -y install mysql-client
RUN apt-get -y install wget
RUN wget https://www.python.org/ftp/python/3.6.2/Python-3.6.2.tar.xz && tar -xvf ./Python-3.6.2.tar.xz
RUN cd ./Python-3.6.2 && ./configure --prefix=/opt/Python-3.6.2 --enable-loadable-sqlite-extensions && make && make install
RUN /opt/Python-3.6.2/bin/pip3.6 install virtualenv
RUN /opt/Python-3.6.2/bin/virtualenv venv_py_3.6.2 -p /opt/Python-3.6.2/bin/python3.6
RUN /bin/bash -c "source ./venv_py_3.6.2/bin/activate && pip install ipython && pip install pandas && pip install mysqlclient && pip install django"
#COPY docker_demo_project/ docker_demo_project/
#ENTRYPOINT ["/bin/bash", "-c", "source ./venv_py_3.6.2/bin/activate && cd docker_demo_project/ && python manage.py runserver 0.0.0.0:9000"]
#COPY ./web_env ./web_env
COPY ./kattegat/ ./kattegat/
RUN /bin/bash -c "mkdir /log_download"
ENTRYPOINT ["/bin/bash", "-c", "source ./venv_py_3.6.2/bin/activate && cd ./kattegat/ && python ./wait_for_port.py -i $DB_CONTAINER_NAME -p 3306 -c 60 && python manage.py migrate && cd ./vplex/err_code_xml/ && python ./err_code_xml_parser.py -f VPlexErrCode.bin.Debug.50.xml -v 5.0 && python ./err_code_xml_parser.py -f VPlexErrCode.bin.Debug.51.xml -v 5.1 && python ./err_code_xml_parser.py -f VPlexErrCode.bin.Debug.52.xml -v 5.2 && python ./err_code_xml_parser.py -f VPlexErrCode.bin.Debug.53.xml -v 5.3 && python ./err_code_xml_parser.py -f VPlexErrCode.bin.Debug.54.xml -v 5.4 && python ./err_code_xml_parser.py -f VPlexErrCode.bin.Debug.55.xml -v 5.5 && python ./err_code_xml_parser.py -f VPlexErrCode.bin.Debug.60.xml -v 6.0 && cd ../.. && python manage.py runserver 0.0.0.0:$WEB_PORT"]

################################################################################################################################################
# sudo docker run -e CDLOG_FILE=FNM00161700007-c1-diagnostics-2018-04-15-02.16.34.tar.gz --volume /log_download:/log_download vplex_log_server #
################################################################################################################################################
FROM ubuntu:16.04
MAINTAINER horst.wang@emc.com

RUN apt-get update
RUN apt-get -y install wget
RUN apt-get install zlib1g zlib1g-dev -y
RUN apt-get install libssl-dev -y
RUN apt-get install openssl -y
RUN apt-get install build-essential -y
RUN apt-get install libsqlite3-dev -y
RUN apt-get -y install libmysqlclient-dev
RUN apt-get -y install mysql-client
RUN apt-get -y install nmap
RUN apt-get -y install libsm6 libxrender1 libfontconfig1 -y
RUN /bin/bash -c "wget https://www.python.org/ftp/python/2.7.10/Python-2.7.10.tgz && tar xvf Python-2.7.10.tgz"
RUN /bin/bash -c "cd ./Python-2.7.10/"
RUN cd ./Python-2.7.10 && ./configure --prefix=/opt/Python-2.7.10 --with-zlib=/usr/include && sed -i 's/#zlib zlibmodule.c/zlib zlibmodule.c/g' ./Modules/Setup && sed -i 's/#_sha256 sha256module.c/_sha256 sha256module.c/g' ./Modules/Setup && sed -i 's/#_sha512 sha512module.c/_sha512 sha512module.c/g' ./Modules/Setup && make && make install
RUN cd /opt/Python-2.7.10/bin && ./python --version
RUN cd /opt/Python-2.7.10/bin && wget https://bootstrap.pypa.io/get-pip.py --no-check-certificate && ./python ./get-pip.py --trusted-host pypi.python.org && ./pip install mysqlclient
RUN /bin/bash -c "mkdir /LogAnalysis"
COPY ./VPLEXLogAnalysisTool-D4_ZLA_80-0.tar /LogAnalysis/VPLEXLogAnalysisTool-D4_ZLA_80-0.tar
COPY ./kattegat/ ./kattegat/
COPY ./rolling_job.py /LogAnalysis/rolling_job.py
RUN /bin/bash -c "cd /LogAnalysis/ && tar xvf ./VPLEXLogAnalysisTool-D4_ZLA_80-0.tar"
RUN /bin/bash -c "mkdir /log_download"
#ENTRYPOINT ["/bin/bash", "-c", "export PATH=/opt/Python-2.7.10/bin:$PATH && cd /log_download && /LogAnalysis/logAnalysisTool.sh -l /tmp/log.txt $CDLOG_FILE"]
#ENTRYPOINT ["/bin/bash", "-c", "cd /log_download && /LogAnalysis/logAnalysisTool.sh -l /tmp/log.txt $CDLOG_FILE"]
ENTRYPOINT ["/bin/bash", "-c", "export PATH=/opt/Python-2.7.10/bin:$PATH && cd ./kattegat/ && python ./wait_for_port.py -i $DB_CONTAINER_NAME -p 3306 -c 60 && cd /log_download && python /LogAnalysis/rolling_job.py"]

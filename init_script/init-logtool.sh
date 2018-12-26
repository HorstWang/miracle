#/bin/bash

sudo mkdir /LogAnalysis
sudo cp ./VPLEXLogAnalysisTool-D4_ZLA_80-0.tar /LogAnalysis/
sudo cp ../docker_script/docker-logserver/rolling_job.py /LogAnalysis/
cd /LogAnalysis/
sudo tar xvf ./VPLEXLogAnalysisTool-D4_ZLA_80-0.tar

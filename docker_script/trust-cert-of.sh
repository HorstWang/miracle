#/bin/bash

SITE_NAME=storage.googleapis.com

ex +'/BEGIN CERTIFICATE/,/END CERTIFICATE/p' <(echo | openssl s_client -showcerts -connect $SITE_NAME:443) -scq > $SITE_NAME.crt
sudo cp ./$SITE_NAME.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
sudo systemctl restart docker

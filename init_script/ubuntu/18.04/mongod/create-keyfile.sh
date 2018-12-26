#/bin/bash

keyfile=$HOME/keyfile.key
openssl rand -base64 756 > $keyfile
if [ -e "$keyfile" ]
then
  echo 'Key file saved to '$keyfile
else
  echo 'Failed to generate key file.'
fi

#/bin/bash

build_db_image()
{
  IMG_NAME=$1
  TAG=$2

  cd ./docker-mysql/
  sudo docker build -t $IMG_NAME:$TAG .
  cd ..
}

run_db_container()
{
  IMG_NAME=$1
  CONTNR_NAME=$2
  TAG=$3
  
  sudo docker run --name $CONTNR_NAME -d $IMG_NAME:$TAG
}

run_db_container_from_hub()
{
  REPO=$1
  IMG_NAME=$2
  CONTNR_NAME=$3
  TAG=$4
  
  sudo docker run --name $CONTNR_NAME -d $REPO/$IMG_NAME:$TAG
}

#commit_db_container()
#{
#  DB_IMG_NAME=$1
#  DB_CONTNR_NAME=$2
#  TAG=$3
#
#  DB_CONTNR_ID=$(sudo docker ps -a | grep $DB_CONTNR_NAME | awk '{ print $1 }')
#  sudo docker commit $DB_CONTNR_ID $DB_IMG_NAME:$TAG
#}

build_web_image()
{
  WEB_IMG_NAME=$1
  TAG=$2

# echo "export DB_CONTAINER_NAME=$DB_CONTNR_NAME" > ./docker-django/web_env
  cd ./docker-django/
  cp -r ../../kattegat/ ./
  sudo docker build -t $WEB_IMG_NAME:$TAG .
  rm -rf ./kattegat/
  cd ..
}

run_web_container()
{
  WEB_IMG_NAME=$1
  WEB_CONTNR_NAME=$2
  WEB_P=$3
  DB_IMG_NAME=$4
  DB_CONTNR_NAME=$5
  TAG=$6

# sudo docker run --name $WEB_CONTNR_NAME --link $DB_CONTNR_NAME:$DB_IMG_NAME -e DB_CONTAINER_NAME=$DB_CONTNR_NAME -e WEB_PORT=$WEB_P -p $WEB_P:$WEB_P -d $WEB_IMG_NAME:latest
  sudo docker run --name $WEB_CONTNR_NAME --link $DB_CONTNR_NAME:$DB_CONTNR_NAME -e DB_CONTAINER_NAME=$DB_CONTNR_NAME -e WEB_PORT=$WEB_P -p $WEB_P:$WEB_P -d $WEB_IMG_NAME:$TAG
}

run_web_container_from_hub()
{
  REPO=$1
  WEB_IMG_NAME=$2
  WEB_CONTNR_NAME=$3
  WEB_P=$4
  DB_IMG_NAME=$5
  DB_CONTNR_NAME=$6
  TAG=$7

# sudo docker run --name $WEB_CONTNR_NAME --link $DB_CONTNR_NAME:$DB_IMG_NAME -e DB_CONTAINER_NAME=$DB_CONTNR_NAME -e WEB_PORT=$WEB_P -p $WEB_P:$WEB_P -d $WEB_IMG_NAME:latest
  sudo docker run --name $WEB_CONTNR_NAME --link $DB_CONTNR_NAME:$DB_CONTNR_NAME -e DB_CONTAINER_NAME=$DB_CONTNR_NAME -e WEB_PORT=$WEB_P -p $WEB_P:$WEB_P -d $REPO/$WEB_IMG_NAME:$TAG
}

build_logserver_image()
{
  WEB_IMG_NAME=$1
  TAG=$2

# echo "export DB_CONTAINER_NAME=$DB_CONTNR_NAME" > ./docker-django/web_env
  cd ./docker-logserver/
  cp -r ../../kattegat/ ./
  sudo docker build -t $WEB_IMG_NAME:$TAG .
  rm -rf ./kattegat/
  cd ..
}

init_db()
{
  WEB_IMG_NAME=$1
  WEB_P=$2

  WEB_APP_CONTAINER_ID=$(sudo docker ps -a | grep $WEB_IMG_NAME\_$WEB_P | grep -v /$WEB_IMG_NAME | awk '{ print $1 }')
  sudo docker exec $WEB_APP_CONTAINER_ID /bin/bash -c "source ./venv_py_3.6.2/bin/activate && cd ./kattegat/vplex/err_code_xml/ && python ./err_code_xml_parser.py -f VPlexErrCode.bin.Debug.50.xml -v 5.0 && python ./err_code_xml_parser.py -f VPlexErrCode.bin.Debug.51.xml -v 5.1 && python ./err_code_xml_parser.py -f VPlexErrCode.bin.Debug.52.xml -v 5.2 && python ./err_code_xml_parser.py -f VPlexErrCode.bin.Debug.53.xml -v 5.3 && python ./err_code_xml_parser.py -f VPlexErrCode.bin.Debug.54.xml -v 5.4 && python ./err_code_xml_parser.py -f VPlexErrCode.bin.Debug.55.xml -v 5.5 && python ./err_code_xml_parser.py -f VPlexErrCode.bin.Debug.60.xml -v 6.0 && deactivate && cd ~"
}

commit_container()
{
  IMG_NAME=$1
  CONTNR_NAME=$2
  TAG=$3

  APP_CONTAINER_ID=$(sudo docker ps -a | grep $CONTNR_NAME | awk '{ print $1 }')
  echo "Commiting container $APP_CONTAINER_ID as $IMG_NAME:$TAG..."
  sudo docker commit $APP_CONTAINER_ID $IMG_NAME:$TAG
}

docker_hub_login()
{
  sudo docker login
}

push_image()
{
  REPO=$1
  IMG_NAME=$2
  TAG=$3

  IMG_ID=$(sudo docker images -a | grep $IMG_NAME | grep $TAG | grep -v /$IMG_NAME | awk '{ print $3 }')
  echo "We are pushing image $IMG_ID ..."
  if [ "$IMG_ID" == '' ]
  then
    echo "Cannot find image $DB_IMG_NAME:$TAG!"
  else
    echo "Login to hub.docker.com ..."
    sudo docker tag $IMG_ID $REPO/$IMG_NAME:$TAG
    sudo docker push $REPO/$IMG_NAME:$TAG
  fi
}

ACTION=$1
WEB_PORT=10000
IMAGE_TAG=$2
PROD_WEB_PORT=$3
DB_IMAGE_NAME=vplex_log_db
WEB_IMAGE_NAME=vplex_log_parser
LOGSERVER_IMAGE_NAME=vplex_log_server
DB_CONTAINER_NAME=$DB_IMAGE_NAME\_$WEB_PORT
WEB_CONTAINER_NAME=$WEB_IMAGE_NAME\_$WEB_PORT
LOGSERVER_CONTAINER_NAME=$LOGSERVER_IMAGE_NAME\_$WEB_PORT
PROD_DB_CONTAINER_NAME=$DB_IMAGE_NAME\_$PROD_WEB_PORT
PROD_WEB_CONTAINER_NAME=$WEB_IMAGE_NAME\_$PROD_WEB_PORT
REPO_NAME=activemauney

echo "ACTION=$ACTION"
echo "WEB_PORT=$WEB_PORT"
echo "DB_IMAGE_NAME=$DB_IMAGE_NAME"
echo "WEB_IMAGE_NAME=$WEB_IMAGE_NAME"
echo "DB_CONTAINER_NAME=$DB_CONTAINER_NAME"
echo "WEB_CONTAINER_NAME=$WEB_CONTAINER_NAME"

#build_and_run_db $DB_IMAGE_NAME $DB_CONTAINER_NAME
#build_and_run_web $WEB_IMAGE_NAME $WEB_CONTAINER_NAME $WEB_PORT $DB_IMAGE_NAME $DB_CONTAINER_NAME

if [ "$ACTION" == 'build' ]
then
  echo "Building base images with tag $IMAGE_TAG"
  build_db_image $DB_IMAGE_NAME $IMAGE_TAG
  build_web_image $WEB_IMAGE_NAME $IMAGE_TAG
  build_logserver_image $LOGSERVER_IMAGE_NAME $IMAGE_TAG
elif [ "$ACTION" == 'init' ]
then
  if [ "$WEB_PORT" == '' ]
  then
    echo "Must specify valid web port number!"
  else
    echo "Starting containers on port $WEB_PORT for initialize production images"
    run_db_container $DB_IMAGE_NAME $DB_CONTAINER_NAME $IMAGE_TAG
    sleep 10
    run_web_container $WEB_IMAGE_NAME $WEB_CONTAINER_NAME $WEB_PORT $DB_IMAGE_NAME $DB_CONTAINER_NAME $IMAGE_TAG
    sleep 60
    init_db $WEB_IMAGE_NAME $WEB_PORT
    run_web_container $LOGSERVER_IMAGE_NAME $LOGSERVER_CONTAINER_NAME 10001 $DB_IMAGE_NAME $DB_CONTAINER_NAME $IMAGE_TAG
  fi
elif [ "$ACTION" == 'commit' ]
then
  commit_container $WEB_IMAGE_NAME $WEB_CONTAINER_NAME $IMAGE_TAG
  commit_container $DB_IMAGE_NAME $DB_CONTAINER_NAME $IMAGE_TAG
  commit_container $LOGSERVER_IMAGE_NAME $LOGSERVER_CONTAINER_NAME $IMAGE_TAG
elif [ "$ACTION" == 'pull' ]
then
  for image in 'vplex_log_db' 'vplex_log_parser' 'vplex_log_server';do sudo docker pull activemauney/$image:$IMAGE_TAG; done
elif [ "$ACTION" == 'push' ]
then
  docker_hub_login
  push_image $REPO_NAME $DB_IMAGE_NAME $IMAGE_TAG
  push_image $REPO_NAME $WEB_IMAGE_NAME $IMAGE_TAG
  push_image $REPO_NAME $LOGSERVER_IMAGE_NAME $IMAGE_TAG
elif [ "$ACTION" == 'purge' ]
then
  ./purge_all_containers.sh 2>&1 >/dev/null
  ./purge_all_images.sh 2>&1 >/dev/null
elif [ "$ACTION" == 'run' ]
then
  docker_hub_login
  run_db_container_from_hub $REPO_NAME $DB_IMAGE_NAME $PROD_DB_CONTAINER_NAME $IMAGE_TAG
# sleep 10
  run_web_container_from_hub $REPO_NAME $WEB_IMAGE_NAME $PROD_WEB_CONTAINER_NAME $PROD_WEB_PORT $DB_IMAGE_NAME $PROD_DB_CONTAINER_NAME $IMAGE_TAG
else
  echo "'$ACTION' is not a supported action, available options are 'build' and 'init' and 'commit' and 'push' and 'purge' and 'run'."
fi

#!/bin/bash

container_name=$1

docker kill $container_name
docker pull registry.miem.hse.ru/nvr/autorecord/autorec:latest
docker run -d \
 -it \
 --restart on-failure \
 --name $container_name \
 -e ENV_FILE_PATH=/env_files/.env_$container_name \
 --net=host \
 -v /creds:/autorecord/creds \
 -v /env_files:/env_files:ro \
 registry.miem.hse.ru/nvr/autorecord/autorec:latest

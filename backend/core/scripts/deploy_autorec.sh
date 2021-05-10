#!/bin/bash

container_name=$1

docker kill $container_name
docker pull registry.miem.hse.ru/nvr/autorecord/autorec:latest
docker run -d \
 -it \
 --restart on-failure \
 --name $container_name \
 --env-file /env_files/.env_$container_name \
 --net=host \
 -v /creds:/autorecord/creds \
 registry.miem.hse.ru/nvr/autorecord/autorec:latest

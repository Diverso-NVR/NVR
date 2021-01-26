#!/bin/bash

docker-compose kill
docker-compose rm -f
docker-compose build --no-cache
docker-compose up -d

status=$?

if [[ "$status" == 0 ]]; then
  rm -rf ./frontend/dist
  docker cp nvr-app:/dist ./frontend/
  exit 0
fi
echo "Unable to deploy NVR Core"
exit 1

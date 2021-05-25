#!/bin/bash

container_name=$1

docker kill $container_name
docker rm $container_name

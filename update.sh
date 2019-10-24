#!/bin/bash

git pull

docker build -t tello-mqtt-gateway .
docker stop tello-mqtt-gateway >> /dev/null
docker rm tello-mqtt-gateway >> /dev/null

docker run -d --restart always --name tello-mqtt-gateway tello-mqtt-gateway


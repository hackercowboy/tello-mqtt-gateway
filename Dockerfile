FROM python

ADD bin /opt/tello-mqtt-gateway/bin
ADD LICENSE /opt/tello-mqtt-gateway/LICENSE
ADD README.rst /opt/tello-mqtt-gateway/README.rst
ADD setup.py /opt/tello-mqtt-gateway/setup.py
ADD tello_mqtt_gateway /opt/tello-mqtt-gateway/tello_mqtt_gateway

RUN cd /opt/tello-mqtt-gateway;ls -la;python setup.py install

CMD ["tello-mqtt-gateway"]
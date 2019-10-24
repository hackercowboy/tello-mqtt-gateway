FROM python

ADD * /opt/tello-mqtt-gateway

RUN cd /opt/tello-mqtt-gateway;python setup.py install

CMD ["tello-mqtt-gateway"]
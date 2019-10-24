import time
import sys
import json
from tello_mqtt_gateway.server import Server
from tello_mqtt_gateway.server import Drone

server = Server()
server.start()


# drone = Drone('daniel', '192.168.2.35', 9000, True)

# drone.send('command')
# time.sleep(5)
# drone.send('takeoff')
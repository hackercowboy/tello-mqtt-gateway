import socket
import sys
import time
import traceback
import os
import paho.mqtt.client as mqtt
import subprocess as sp

from threading import Thread

class Logable:
    debug = False

    def __init__(self, debug):
        self.debug = debug

    def verbose(self, message):
        if self.debug:
            sys.stdout.write('VERBOSE: ' + message + '\n')
            sys.stdout.flush()

    def error(self, message):
        sys.stderr.write('ERROR: ' + message + '\n')
        sys.stderr.flush()

class Drone(Logable):
    name = None
    ip = None
    local_port = None
    command_socket = None
    command_receive_thread = None
    ping_thread = None
    connected = False
    server = False

    def __init__(self, name, ip, local_port, server, debug):
        super().__init__(debug)
        self.name = name
        self.ip = ip
        self.local_port = local_port
        self.server = server

        self.command_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.command_socket.bind(('', self.local_port))

        self.start_command_receive_thread()
        self.start_ping_thread()

    def send(self, command):
        if self.command_socket != None:
            self.verbose('Will send command ' + command + ' to ' + self.name)
            address = (self.ip, 8889)
            message = command.encode(encoding="utf-8")
            self.command_socket.sendto(message, address)
        else:
            self.error('cant send message to drone ' + self.name + ' cause command_socket is none!')

    def start_command_receive_thread(self):
        self.command_receive_thread = Thread(target=self.on_command_receive_thread)
        self.command_receive_thread.start()

    def start_ping_thread(self):
        self.ping_thread = Thread(target=self.on_ping_thread)
        self.ping_thread.start()

    def on_command_receive_thread(self):
        self.verbose('Will wait for feedback from drone ' + self.name)
        while True: 
            try:
                data, _server = self.command_socket.recvfrom(1518)
                print(data.decode(encoding="utf-8"))
                self.server.send_feedback('/drones/' + self.name, data.decode(encoding="utf-8"))
            except Exception:
                self.error('Receive thread from drone ' + self.name + 'did die')
                self.start_command_receive_thread()
                break

    def on_ping_thread(self):
        self.verbose('Will wait for feedback from drone ' + self.name)
        while True: 
            try:
                status, _result = sp.getstatusoutput("ping -c1 " + self.ip)
                if status == 0:
                    if self.connected != True:
                        self.verbose('Drone got online! ' + self.name)
                        self.send('command')
                        self.server.send_feedback('/drones/' + self.name, 'connected')

                    self.connected = True
                else:
                    if self.connected == True:
                        self.verbose('Drone went offline! ' + self.name)
                        self.server.send_feedback('/drones/' + self.name, 'disconnected')
                    self.connected = False
                
                time.sleep(0.5)
            except Exception as e:
                print(e)
                self.error('Receive thread from drone ' + self.name + 'did die')
                self.start_ping_thread()
                break

class Server(Logable):
    config = None
    mqtt_client = None
    mqtt_connected = False
    drones = None

    def __init__(self):
        super().__init__(True)
        self.debug = True
        self.mqtt_host = '192.168.2.38'
        self.mqtt_port = '1883'
        self.mqtt_client_id = 'drone-gateway'
        self.drones = [
            Drone('daniel', '192.168.2.35', 9000, self, self.debug),
            Drone('peter', '192.168.2.36', 9001, self,  self.debug)
        ]

    def mqtt_connect(self):
        if self.mqtt_broker_reachable():
            self.verbose('Connecting to ' + self.mqtt_host + ':' + self.mqtt_port)
            self.mqtt_client = mqtt.Client(self.mqtt_client_id)
            self.mqtt_client.on_connect = self.mqtt_on_connect
            self.mqtt_client.on_message = self.mqtt_on_message
            self.mqtt_client.on_disconnect = self.mqtt_on_disconnect

            try:
                self.mqtt_client.connect(self.mqtt_host, int(self.mqtt_port), 10)
                self.mqtt_client.loop_forever()
            except:
                self.error(traceback.format_exc())
                self.mqtt_client = None
        else:
            self.error(self.mqtt_host + ':' + self.mqtt_port + ' not reachable!')

    def mqtt_on_connect(self, mqtt_client, userdata, flags, rc):
        self.mqtt_connected = True
        self.verbose('...mqtt_connected!')
        for drone in self.drones:
            self.mqtt_client.subscribe('/drones/' + drone.name + '/send')

    def mqtt_on_disconnect(self, mqtt_client, userdata, rc):
        self.mqtt_connected = False
        self.verbose('Diconnected! will reconnect! ...')
        if rc is 0:
            self.mqtt_connect()
        else:
            time.sleep(5)
            while not self.mqtt_broker_reachable():
                time.sleep(10)
            self.mqtt_client.reconnect()

    def mqtt_broker_reachable(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect((self.mqtt_host, int(self.mqtt_port)))
            s.close()
            return True
        except socket.error:
            return False

    def send_feedback(self, topic, message):
        if self.mqtt_connected:
            self.mqtt_client.publish(topic, message, 2, True)
    

    def mqtt_on_message(self, mqtt_client, userdata, mqtt_message):
        drone_name = mqtt_message.topic.split('/')[2]
        command = mqtt_message.payload.decode()
        self.verbose('Got mqtt message(' + mqtt_message.topic +'): ' +  command + ' will send it to drone ' + drone_name)
        for drone in self.drones:
            if drone.name == drone_name:
                drone.send(command)

    def start(self):
        self.mqtt_connect()

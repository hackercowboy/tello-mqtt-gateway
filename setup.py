# -*- coding: utf-8 -*-
from setuptools import setup


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='tello_mqtt_gateway',
    version='0.0.1',
    description='Mqtt gateway to control a tello drone',
    long_description=readme,
    author='David Uebelacker',
    author_email='david@uebelacker.ch',
    url='git@github.com:hackercowboy/tello-mqtt-gateway.git',
    license=license,
    packages=['tello_mqtt_gateway'],
    install_requires=['paho-mqtt'],
    scripts=['bin/tello-mqtt-gateway']
)
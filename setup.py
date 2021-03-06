from __future__ import unicode_literals
from setuptools import setup, find_packages

setup(
    name='weather_station',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Click',
        'pigpio',
        'paho-mqtt',
        'Adafruit_PureIO',
        'adafruit-circuitpython-bme680',
        'w1thermsensor',
    ],
    entry_points='''
        [console_scripts]
        weather_station=weather_station.cli:cli
    ''',
)

import json
import paho.mqtt.client as mqtt
from .sensors import anemometer, rainfall, wind_vane


class WeatherStationApplication:
    def __init__(self, tb_access_token, tb_host, tb_port=1883):
        self.tb_client = None
        self.tb_access_token = tb_access_token
        self.tb_host = tb_host
        self.tb_port = tb_port

        self.anemometer_1 = anemometer.Anemometer(report_function=self.report)
        self.rainfall_1 = rainfall.Rainfall(report_function=self.report)
        self.wind_vane_1 = wind_vane.WindVane(report_function=self.report)

    def start(self):
        self.anemometer_1.start()
        self.rainfall_1.start()
        self.wind_vane_1.start()

    def _setup_report_connection(self):
        if self.tb_client:
            return
        self.tb_client = client = mqtt.Client()
        client.username_pw_set(self.tb_access_token)
        client.connect(self.tb_host, self.tb_port, 60)
        client.loop_start()

    def report(self, data, ts=None):
        self._setup_report_connection()
        # FIXME: handle ts
        self.tb_client.publish('v1/devices/me/telemetry', json.dumps(data), 1)


def start():
    anemometer_1 = anemometer.Anemometer()
    anemometer_1.start()

    rainfall_1 = rainfall.Rainfall()
    rainfall_1.start()

    wind_vane_1 = wind_vane.WindVane()
    wind_vane_1.start()

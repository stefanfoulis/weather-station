import datetime
import json
import paho.mqtt.client as mqtt
import calendar
from .sensors import anemometer, rainfall, wind_vane, temperature, bme680


def now(delta=None):
    d = datetime.datetime.utcnow()
    if delta:
        d = d + delta
    unixtime = calendar.timegm(d.utctimetuple())
    return unixtime * 1000


class WeatherStationApplication:
    def __init__(self, tb_access_token=None, tb_host=None, tb_port=1883):
        self.tb_client = None
        self.tb_access_token = tb_access_token
        self.tb_host = tb_host
        self.tb_port = tb_port

        self.anemometer_1 = anemometer.Anemometer(report_function=self.report)
        self.rainfall_1 = rainfall.Rainfall(report_function=self.report)
        self.wind_vane_1 = wind_vane.WindVane(report_function=self.report)
        # self.temperature_1 = temperature.Temperature(report_function=self.report)
        self.bme680_1 = bme680.BME680(report_function=self.report)

    def start(self):
        self.anemometer_1.start()
        self.rainfall_1.start()
        self.wind_vane_1.start()
        # self.temperature_1.start()
        self.bme680_1.start()

    def _setup_report_connection(self):
        if self.tb_client:
            return
        if self.tb_host and self.tb_access_token:
            self.tb_client = client = mqtt.Client()
            client.username_pw_set(self.tb_access_token)
            client.connect(self.tb_host, self.tb_port, 60)
            client.loop_start()
        else:
            return

    def report(self, data, ts=None):
        self._setup_report_connection()
        prettydata = " ".join([
            f"{key}: {value}" for key, value in sorted(data.items())
        ])
        print(f"[{datetime.datetime.fromtimestamp(ts)}] {prettydata}")

        if not self.tb_client:
            return
        payload = {
            "ts": now(),
            "values": data,
        }
        self.tb_client.publish(
            "v1/devices/me/telemetry", json.dumps(payload), 1
        )


def start():
    anemometer_1 = anemometer.Anemometer()
    anemometer_1.start()

    rainfall_1 = rainfall.Rainfall()
    rainfall_1.start()

    wind_vane_1 = wind_vane.WindVane()
    wind_vane_1.start()

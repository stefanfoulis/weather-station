import threading
import time

from w1thermsensor import W1ThermSensor


REPORT_INTERVAL_S = 5


class Temperature(threading.Thread):
    def __init__(self, report_function):
        threading.Thread.__init__(self)
        self.report_function = report_function
        # all these 1-wire sensor are connected to GPIO Pin 4
        self.sensor = W1ThermSensor()

    def get_temperature(self):
        return self.sensor.get_temperature()

    def run(self):
        while True:
            temperature_c = self.get_temperature()
            self.report(temperature_c=temperature_c, ts=time.time())
            time.sleep(REPORT_INTERVAL_S)

    def report(self, temperature_c, ts=None):
        return self.report_function(
            data={"temperature_underground_c": temperature_c}, ts=ts
        )

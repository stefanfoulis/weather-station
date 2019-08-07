# TODO: Find out if we could use pigpio or gpiozero instead of circuitpython to access the sensor
#       (just to be consistent)
import threading, time

import board
import busio
import adafruit_bme680


REPORT_INTERVAL_S = 5


class BME680(threading.Thread):
    def __init__(self, report_function):
        threading.Thread.__init__(self)
        self.report_function = report_function
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_bme680.Adafruit_BME680_I2C(self.i2c)

    def get_readings(self):
        return {
            "temperature_c": round(self.sensor.temperature, 1),
            "gas_ohms": self.sensor.gas,
            "humidity_pct": round(self.sensor.humidity, 1),
            "pressure_hpa": round(self.sensor.pressure, 1),
        }

    def run(self):
        while True:
            self.report_function(data=self.get_readings(), ts=time.time())
            time.sleep(REPORT_INTERVAL_S)

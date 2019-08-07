import time
import logging

import pigpio  # http://abyz.co.uk/rpi/pigpio/python.html

logging.basicConfig(
    filename="log_weather.log",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
    datefmt="%d/%m/%Y %I:%M:%S %p",
)

PIN = 18

# Measured: 20 ticks are 100ml. So 1 tick means 5ml.
BUCKET_SIZE_ML = 5.0
FUNNEL_DIAMETER_CM = 8.9


def calculate_mm_per_bucket(
    funnel_diameter_cm=FUNNEL_DIAMETER_CM, bucket_ml=BUCKET_SIZE_ML
):
    # 1mm on 1m^2 means 1mm (and is 1l of water)
    import math

    funnel_area_cm2 = math.pi * (funnel_diameter_cm / 2) ** 2
    factor_from_our_area_to_1m2 = 1000 / funnel_area_cm2
    rain_amount_ml_on_1m2 = bucket_ml * factor_from_our_area_to_1m2
    rain_amount_l_on_1m2 = rain_amount_ml_on_1m2 / 1000
    rain_amount_mm = rain_amount_l_on_1m2
    return rain_amount_mm


BUCKET_SIZE_MM = 0.08  # calculated with calculate_mm_per_bucket(8.9, 5.0)

GLITCH_MICROSECONDS = 1000  # 1ms

MIN_REPORT_INTERVAL_S = 1


def calculate_rainfall(tick_count):
    return tick_count * BUCKET_SIZE_MM


def calculate_rainfall_per_hour(rain_amount_mm, duration_s):
    rain_amount_mm_per_h = (rain_amount_mm / duration_s) * (60 * 60)
    return rain_amount_mm_per_h


class Rainfall:
    def __init__(self, report_function, pin=PIN):
        self.pin = pin
        self.report_function = report_function
        self.last_tick_at = time.time()
        self.tick_count = 0
        self.pi = pigpio.pi()
        self.callback = None
        self.setup_hardware()

    def start(self):
        self.callback = self.pi.callback(self.pin, pigpio.RISING_EDGE, self.handle_tick)

    def stop(self):
        if self.callback:
            self.callback.cancel()

    def setup_hardware(self):
        if not self.pi.connected:
            logging.critical("Cannot connect to pigpio-pi")

        self.pi.set_mode(self.pin, pigpio.INPUT)
        self.pi.set_pull_up_down(self.pin, pigpio.PUD_UP)
        self.pi.set_glitch_filter(self.pin, GLITCH_MICROSECONDS)  # Ignore glitches.

    def handle_tick(self, gpio, level, tick):
        current_tick_at, previous_tick_at = time.time(), self.last_tick_at
        duration_s = current_tick_at - previous_tick_at
        self.tick_count += 1

        if duration_s < MIN_REPORT_INTERVAL_S:
            # Don't report more than once every MIN_REPORT_INTERVAL_S.
            # Just record the tick.
            return
        rain_amount_mm = calculate_rainfall(tick_count=self.tick_count)
        rain_amount_mm = round(rain_amount_mm, 2)
        if duration_s:
            rain_amount_mm_per_h = round(
                calculate_rainfall_per_hour(rain_amount_mm, duration_s), 2
            )
        else:
            rain_amount_mm_per_h = None
        self.report(
            rain_amount_mm=rain_amount_mm,
            rain_amount_mm_per_h=rain_amount_mm_per_h,
            ts=current_tick_at,
        )
        # Reset counts for next report
        self.tick_count = 0
        self.last_tick_at = current_tick_at

    def report(self, rain_amount_mm, rain_amount_mm_per_h, ts):
        data = {"rain_amount_mm": rain_amount_mm}
        if rain_amount_mm_per_h is not None:
            data["rain_amount_mm_per_h"] = rain_amount_mm_per_h
        self.report_function(data=data, ts=ts)

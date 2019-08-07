# FIXME: send a value of 0 if no ticks have been registered for so long that the speed on the next tick
#        would be close to zero.
import math
import time
import logging

import pigpio  # http://abyz.co.uk/rpi/pigpio/python.html

logging.basicConfig(
    filename="log_weather.log",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
    datefmt="%d/%m/%Y %I:%M:%S %p",
)

PIN_ANEMOMETER = 22

RADIUS_CM = 9.0
# ¯\_(ツ)_/¯ I was so sure SIGNALS_PER_ROTATION was 2. But now measuring real values
# indicate we're off by a factor of 2 (half the expected wind speeds). I don't want to
# climb up to the weather station and test right now. Maybe later.
# Changing to 1 now.
SIGNALS_PER_ROTATION = 1
CORRECTION_FACTOR = 1.18
CALCULACTION_INTERVAL_S = 5

CIRCUMFERENCE_CM = (2 * math.pi) * RADIUS_CM

GLITCH_MICROSECONDS = 1000  # 1ms

MIN_REPORT_INTERVAL_S = 0.5
COUNT_AS_0_TIMEOUT_MS = 5000


def calculate_speed(
    duration_s,
    tick_count,
    ticks_per_rotation=SIGNALS_PER_ROTATION,
    circumference_cm=CIRCUMFERENCE_CM,
    correction_factor=CORRECTION_FACTOR,
):
    rotations = tick_count / ticks_per_rotation
    dist_cm = circumference_cm * rotations
    speed = dist_cm / duration_s
    return speed * correction_factor


def cm_per_s_to_km_per_h(cm_per_s):
    return cm_per_s * 60 * 60 / 100 / 1000


class Anemometer:
    def __init__(self, report_function, pin=PIN_ANEMOMETER):
        self.pin = pin
        self.report_function = report_function
        self.last_tick_at = time.time()
        self.tick_count = 0
        self.pi = pigpio.pi()
        self.callback = None
        self.watchdog = None
        self.setup_hardware()

    def start(self):
        self.callback = self.pi.callback(self.pin, pigpio.RISING_EDGE, self.handle_tick)
        self.watchdog = self.pi.set_watchdog(self.pin, COUNT_AS_0_TIMEOUT_MS)

    def stop(self):
        if self.callback:
            self.callback.cancel()
            # FIXME: cancel watchdog

    def setup_hardware(self):
        if not self.pi.connected:
            logging.critical("Cannot connect to pigpio-pi")

        self.pi.set_mode(self.pin, pigpio.INPUT)
        self.pi.set_pull_up_down(self.pin, pigpio.PUD_UP)
        self.pi.set_glitch_filter(self.pin, GLITCH_MICROSECONDS)  # Ignore glitches.

    def handle_tick(self, gpio, level, tick):
        if level == pigpio.TIMEOUT:
            # There has not been any event for COUNT_AS_0_TIMEOUT_MS. Lets
            # report 0 as speed.
            self.report(0, ts=time.time())
            return
        current_tick_at, previous_tick_at = time.time(), self.last_tick_at
        self.tick_count += 1

        duration_s = current_tick_at - previous_tick_at
        if duration_s < MIN_REPORT_INTERVAL_S:
            # Don't report more than once every MIN_REPORT_INTERVAL_S.
            # Just record the tick.
            return
        speed_cms_per_s = calculate_speed(
            duration_s=duration_s, tick_count=self.tick_count
        )
        speed_km_per_h = cm_per_s_to_km_per_h(speed_cms_per_s)
        speed_km_per_h = round(speed_km_per_h, 3)
        self.report(speed_km_per_h, ts=current_tick_at)
        self.tick_count = 0
        self.last_tick_at = current_tick_at

    def report(self, speed_km_per_h, ts):
        self.report_function(data={"wind_speed_km_per_h": speed_km_per_h}, ts=ts)

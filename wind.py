import math
from gpiozero import Button
from signal import pause
import time

wind_speed_sensor = Button(22)
total_signal_count = 0

RADIUS_CM = 9.0
SIGNALS_PER_ROTATION = 2
CORRECTION_FACTOR = 1.18
CALCULACTION_INTERVAL_S = 5

CIRCUMFERENCE_CM = (2 * math.pi) * RADIUS_CM


last_signal = None


def calculate_speed(
        duration_s,
        signal_count,
        signals_per_rotation=SIGNALS_PER_ROTATION,
        circumference_cm=CIRCUMFERENCE_CM,
        correction_factor=CORRECTION_FACTOR,
):
    rotations = signal_count / signals_per_rotation
    dist_cm = circumference_cm * rotations
    speed = dist_cm / duration_s
    return speed * correction_factor


def spin():
    global total_signal_count, last_signal
    if last_signal is None:
        last_signal = time.time()
        # can't calculate yet
        return
    current_signal, previous_signal = time.time(), last_signal
    last_signal = current_signal
    total_signal_count = total_signal_count + 1

    duration_s = current_signal - previous_signal
    speed_cm_per_s = calculate_speed(duration_s=duration_s, signal_count=1)
    speed_km_per_h = speed_cm_per_s * 60 * 60 / 100 / 1000

    print("signals={}  speed={:.0f} cm/s  {:.01f} km/h".format(total_signal_count, speed_cm_per_s, speed_km_per_h))


wind_speed_sensor.when_pressed = spin
pause()

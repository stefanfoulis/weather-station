Installation
============

Download Raspbian and put it on an SD-Card.
Create an empty `ssh` file on the fat partition, so that sshd is started on boot.
Login to the box over `ssh` once it has booted.
Change the Password for the `pi` user!

Install `pyenv` by following http://www.knight-of-pi.org/pyenv-for-python-version-management-on-raspbian-stretch/

Then::

    pyenv install 3.7.2
    cd to/project
    pyenv local 3.7.2
    python -m venv .venv
    source .venv/bin/activate
    pip install pip-tools
    pip install -r requirements.txt


We also need the `pigpio` daemon running::

    sudo apt-get update
    sudo apt-get install pigpio


Start `pigpio` at startup time with `systemd` (ALTERNATIVE: use `sudo raspi-config` to enable "Remote GPIO")::

    sudo systemctl enable pigpiod.service
    sudo reboot


Start `weather_station` at boot time with `systemd`::

    sudo cp weather_station/scripts/systemd/weather_station.service /lib/systemd/system
    sudo chmod 644 /lib/systemd/system/weather_station.service
    sudo systemctl daemon-reload
    sudo systemctl enable weather_station.service
    # create a file named /home/pi/.weather_station_env that contains credentials
    # for thingsboard (WEATHER_STATION_TB_HOST, WEATHER_STATION_TB_PORT, WEATHER_STATION_TB_ACCESS_TOKEN)
    sudo reboot



Connecting some sensors

https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/hardware

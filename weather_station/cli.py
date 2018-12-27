import click
from .app import WeatherStationApplication


@click.command()
@click.option('--tb-host', envvar='WEATHER_STATION_TB_HOST')
@click.option('--tb-port', envvar='WEATHER_STATION_TB_PORT', default=1883)
@click.option('--tb-access-token', envvar='WEATHER_STATION_TB_ACCESS_TOKEN')
def cli(tb_host, tb_port, tb_access_token):
    click.echo('Starting weather station...')
    app = WeatherStationApplication(tb_host=tb_host, tb_port=tb_port, tb_access_token=tb_access_token)
    app.start()

import click
from .app import WeatherStationApplication


@click.group()
def cli():
    pass


@cli.command()
@click.option("--tb-host", envvar="WEATHER_STATION_TB_HOST", default=None)
@click.option("--tb-port", envvar="WEATHER_STATION_TB_PORT", default=1883)
@click.option("--tb-access-token", envvar="WEATHER_STATION_TB_ACCESS_TOKEN", default=None)
@click.option("--tb-user", envvar="WEATHER_STATION_TB_USER", default=None)
def report(tb_host, tb_port, tb_access_token, tb_user):
    click.echo(f"Starting weather station with reporting to {tb_host}...")
    app = WeatherStationApplication(
        tb_host=tb_host, tb_port=tb_port, tb_access_token=tb_access_token, tb_user=tb_user
    )
    app.start()


@cli.command()
def local():
    click.echo("Starting weather station without reporting...")
    app = WeatherStationApplication()
    app.start()


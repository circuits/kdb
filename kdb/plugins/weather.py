# Plugin:   weather
# Date:     01th July 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Weather

This plugin provides weather information from metar
stations around the world to the user.
"""


__version__ = "0.0.2"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from circuits import Component

from funcy import first

from pymetar import ReportFetcher, ReportParser


from ..utils import log
from ..plugin import BasePlugin


class Commands(Component):

    channel = "commands"

    def weather(self, source, target, args):
        """Display weather for the given station

        This looks up the weather information from http://weather.noaa.gov/
        by using metar codes. For a list of station codes see
        http://www.nws.noaa.gov/tg/siteloc.shtml The default
        station is YBBN, Brisbane airport, Australia.

        Syntax: WEATHER [<station>]
        """

        tokens = args.split(" ", 1)
        station = first(tokens) or "YBBN"

        try:
            rf = ReportFetcher(station)
            rep = rf.FetchReport()
        except Exception, e:
            msg = log(
                "ERROR: Could not get weather report for {0:s}: {1:s}",
                station,
                e
            )
            return msg

        rp = ReportParser()
        pr = rp.ParseReport(rep)

        msgs = []

        msgs.append(
            "Weather report for {0:s} ({1:s}) as of {2:s}".format(
                pr.getStationName(),
                station,
                pr.getISOTime()
            )
        )

        msgs.append("Weather: {0:s}".format(pr.getWeather()))
        msgs.append("Sky: {0:s}".format(pr.getSkyConditions()))

        msgs.append(
            "Temperature: {0:0.2f} C / {1:0.2f} F".format(
                pr.getTemperatureCelsius(),
                pr.getTemperatureFahrenheit()
            )
        )

        msgs.append("Humidity: {0:d}%".format(pr.getHumidity()))

        if pr.getWindSpeed() is not None:
            msgs.append(
                "Wind: {0:0.2f} m/s [{1:d} deg ({2:s})]".format(
                    pr.getWindSpeed(),
                    pr.getWindDirection(),
                    pr.getWindCompass()
                )
            )
        else:
            msgs.append("Wind: None")

        if pr.getPressure() is not None:
            msgs.append("Pressure: {0:d} hPa".format(int(pr.getPressure())))
        else:
            msgs.append("Pressure: None")

        msgs.append(
            "Dew: {0:f} C / {1:f} F".format(
                pr.getDewPointCelsius(),
                pr.getDewPointFahrenheit()
            )
        )

        return msgs


class Weather(BasePlugin):
    """Weather plugin

    Provides weather information retrieved from METAR sources.
    The METAR codes are available from:
     - http://www.nws.noaa.gov/tg/siteloc.shtml
    See: help weather
    """

    def init(self, *args, **kwargs):
        super(Weather, self).init(*args, **kwargs)

        Commands().register(self)

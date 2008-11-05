# Module:	weather
# Date:		01th July 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Weather

This plugin provides weather information from metar
stations around the world to the user.
"""

__ver__ = "0.0.2"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import pymetar
from traceback import format_exc

from kdb.plugin import BasePlugin

class Weather(BasePlugin):

	"""Weather plugin

	Provides weather information retrieved from METAR sources.
	The METAR codes are available from:
	 - http://www.nws.noaa.gov/tg/siteloc.shtml
	See: help weather
	"""

	def cmdWEATHER(self, source, station="YBBN"):
		"""Display weather for the given station
		
		This looks up the weather information from http://weather.noaa.gov/
		by using metar codes. For a list of station codes see
		http://www.nws.noaa.gov/tg/siteloc.shtml The default
		station is YBBN, Brisbane airport, Australia.
		
		Syntax: WEATHER [<station>]
		"""

		try:
			rf = pymetar.ReportFetcher(station)
			rep = rf.FetchReport()
		except Exception, e:
			msg = ["ERROR: Could not get weather report for '%s': %s" % (
				station, e), format_exc()]
			return msg

		rp = pymetar.ReportParser()
		pr = rp.ParseReport(rep)

		msg = []
		msg.append("Weather report for %s (%s) as of %s" % (
			pr.getStationName(), station, pr.getISOTime()))

		msg.append("Weather: " + str(pr.getWeather()))
		msg.append("Sky: " + str(pr.getSkyConditions()))

		msg.append("Temp: %s C / %s F" % (
			pr.getTemperatureCelsius(),
			pr.getTemperatureFahrenheit()))

		msg.append("Hum: %s%%" % (pr.getHumidity()))

		if pr.getWindSpeed() is not None:
			msg.append("Wind: %0.2f m/s [%s deg (%s)]" % (
				pr.getWindSpeed(), pr.getWindDirection(),
				pr.getWindCompass()))
		else:
			msg.append("Wind: None")

		if pr.getPressure() is not None:
			msg.append("Pressure: %s hPa" % (int(pr.getPressure())))
		else:
			msg.append("Pressure: None")

		msg.append("Dew: %s C / %s F" % (
			pr.getDewPointCelsius(), pr.getDewPointFahrenheit()))

		return msg

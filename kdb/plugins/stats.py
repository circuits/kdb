# Filename: stats.py
# Module:	stats
# Date:		30th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Statistics

This plugin collects various statistics and allows the
user to access and display them.
"""

__ver__ = "0.0.4"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import time

from pymills.misc import bytes
from pymills.event import filter
from pymills.misc import duration

import kdb
from kdb.plugin import BasePlugin

class Stats(BasePlugin):

	"""Statistics plugin

	Provides various statistical functions and information.
	Namely, network, uptime and error stats.
	See: commands stats
	"""

	def __init__(self, event, bot, env):
		BasePlugin.__init__(self, event, bot, env)

		self.tin = 0
		self.tout = 0

		self.stime = time.time()

	def cmdERRORS(self, source):
		"""Display numbers of errors that have occured
		
		Syntax: ERRORS
		"""

		if self.env.errors == 0:
			msg = "No errors"
		else:
			msg = "Errors: %d" % self.env.errors
		return msg

	def cmdUPTIME(self, source):
		"""Display current uptime and cpu usage
		
		Syntax: UPTIME
		"""

		uptime = duration(time.time() - self.stime)
		cpu = time.clock()
		msg = "Uptime: %s+%s:%s:%s (CPU: %s)" % (uptime + (cpu,))
		return msg
	
	def cmdNSTATS(self, source):
		"""Display current network stats
		
		Syntax: NSTATS
		"""

		msg = "Traffic: (I, O, T) = (%s, %s, %s)" % (
				"%0.2f%s" % (bytes(self.tin)),
				"%0.2f%s" % (bytes(self.tout)),
				"%0.2f%s" % (bytes(self.tin + self.tout)))

		return msg

	def cmdVERSION(self, source):
		"""Display version information
		
		Syntax: VERSION
		"""

		msg = "%s [ %s ] v%s by %s - %s - %s" % (
				kdb.__name__,
				kdb.__description__,
				kdb.__version__,
				kdb.__author_email__,
				kdb.__copyright__,
				kdb.__url__)
		return msg

	@filter("read")
	def onREAD(self, event, line):
		self.tin += len(line) + 2
		return False, event

	@filter("write")
	def onWRITE(self, event, data):
		self.tout += len(data)
		return False, event

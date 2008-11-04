# Module:	stats
# Date:		30th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Statistics

This plugin collects various statistics and allows the
user to access and display them.
"""

__ver__ = "0.2"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import os
import time

from circuits import listener
from pymills.utils import MemoryStats
from pymills.misc import bytes, duration, buildAverage

import kdb
from kdb.plugin import BasePlugin

class Stats(BasePlugin):

	"""Statistics plugin

	Provides various statistical functions and information.
	Namely, network, uptime and error stats.
	See: commands stats
	"""

	def __init__(self, *args, **kwargs):
		super(Stats, self).__init__(*args, **kwargs)

		self.tin = 0
		self.tout = 0
		self.commands = {}

		self.stime = time.time()

	def cmdERRORS(self, source):
		"""Display numbers of errors that have occured
		
		Syntax: ERRORS
		"""

		if self.env.errors == 0:
			msg = "No errors"
		else:
			msg = "Errors: %d" % self.env.errors
		return msg

	def cmdUPTIME(self, source):
		"""Display current uptime and cpu usage
		
		Syntax: UPTIME
		"""

		tTime = time.time() - self.stime
		uptime = duration(tTime)
		cpu = time.clock()
		rate = (cpu / tTime) * 100.0
		msg = "Uptime: %s+%s:%s:%s (CPU: %0.2fs %0.2f%%)" % (
				uptime + (cpu, rate))
		return msg

	def cmdCSTATS(self, source):
		"""Display command usage stats

		Syntax: CSTATS
		"""

		totalCommands = sum(self.commands.values())

		l = list(self.commands.iteritems())[:5]
		l.sort(lambda x, y: x[1] - y[1])
		x = [cmd[0] for cmd in l]
		x.reverse()

		msg = "Command Stats: %s Total: %d Top 5: %s" % (
				buildAverage(self.stime, totalCommands) + (" ".join(x),))

		return msg


	def cmdNSTATS(self, source):
		"""Display current network stats
		
		Syntax: NSTATS
		"""

		msg = "Traffic: (I, O, T) = (%s, %s, %s)" % (
				"%0.2f%s" % (bytes(self.tin)),
				"%0.2f%s" % (bytes(self.tout)),
				"%0.2f%s" % (bytes(self.tin + self.tout)))

		return msg

	def cmdVERSION(self, source):
		"""Display version information
		
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

	def cmdMSTATS(self, source):
		"""Display current memory stats
		
		Syntax: MSTATS
		"""

		m= MemoryStats(os.getpid())

		msg = "Memory: %s %s %s" % (
			"%0.2f%s" % bytes(m.size),
			"%0.2f%s" % bytes(m.rss),
			"%0.2f%s" % bytes(m.stack))

		return msg

	@listener("PostCommand", type="filter")
	def onPOSTCOMMAND(self, command, tokens):
		if not self.commands.has_key(command):
			self.commands[command] = 0
		self.commands[command] += 1

	@listener("read", type="filter")
	def onREAD(self, line):
		self.tin += len(line) + 2

	@listener("write", type="filter")
	def onWRITE(self, data):
		self.tout += len(data)

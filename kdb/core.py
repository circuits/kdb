# Module:	core
# Date:		2nd August 2005
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""core - Core Component

Core management component and main loop handler.
All events are processes by this component and
also handles system signals to help reload the
configuration and terminate the system.
"""

import os
import signal
import socket
from time import sleep
from traceback import format_exc

from circuits import listener, Event, Component
from circuits.lib.log import (
		Debug as LogDebug,
		Exception as LogException)

from pymills.utils import State

###
### Events
###

class Start(Event):
	"""Start(Event) -> Start Event"""

class Run(Event):
	"""Run(Event) -> Run Event"""


class Core(Component):

	channel = "core"

	running = False

	def __init__(self, env):
		super(Core, self).__init__()

		signal.signal(signal.SIGHUP, self.onREHASH)
		signal.signal(signal.SIGTERM, self.onSTOP)

		self.env = env

	@listener("start")
	def onSTART(self):
		self.send(Run(), "run", self.channel)

	@listener("stop")
	def onSTOP(self, signal=0, stack=0):
		if self.env.bot.connected:
			self.env.bot.ircQUIT("Received SIGTERM, terminating...")
		self.running = False

	@listener("rehash")
	def onREHASH(self, signal=0, stack=0):
		self.env.reload()

	@listener("run")
	def onRUN(self):
		self.running = True

		self.env.bot.connect()

		while self.running:
			try:
				self.manager.flush()
				if self.env.bot.connected:
					self.env.bot.poll()
				else:
					sleep(1)
			except KeyboardInterrupt:
				if self.env.bot.connected:
					self.env.bot.ircQUIT("Received ^C, terminating...")
				self.running = False
			except Exception, error:
				self.env.errors += 1
				self.push(LogException("ERROR: %s" % error), "exception", "log")
				self.push(LogDebug(format_exc()), "debug", "log")

		self.env.unloadPlugins()

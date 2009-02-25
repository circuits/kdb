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

from circuits import Event, Component
from circuits.lib.log import (
		Debug as LogDebug,
		Exception as LogException)

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

		signal.signal(signal.SIGHUP, self.rehash)
		signal.signal(signal.SIGTERM, self.stop)

		self.env = env

	def stop(self, signal=0, stack=0):
		if self.env.bot.isConnected():
			self.env.bot.ircQUIT("Received SIGTERM, terminating...")
		self.running = False

	def rehash(self, signal=0, stack=0):
		self.env.reload()

	def error(self, *args, **kwargs):
		if len(args) == 3 and issubclass(args[0], BaseException):
			self.env.errors += 1
			self.push(LogException("ERROR: %s" % args[1]), "exception", "log")
			self.push(LogDebug(args[3]), "debug", "log")

	def run(self):
		self.running = True

		self.env.loadPlugins()

		self.env.bot.connect()

		while self.running:
			try:
				self.manager.flush()

				if self.env.bot.connected:
					self.env.bot.poll()
				else:
					sleep(1)

				self.env.bridge.poll()

				for timer in self.env.timers[:]:
					if timer.manager == self.manager:
						timer.poll()
					else:
						self.env.timers.remove(timer)

			except KeyboardInterrupt:
				if self.env.bot.connected:
					self.env.bot.ircQUIT("Received ^C, terminating...")
				self.running = False

		self.env.unloadPlugins()

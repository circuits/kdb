# Filename: core.py
# Module:	core
# Date:		2nd August 2005
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Core Component

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

from pymills.event import *
from pymills.utils import State

class Core(Component):

	def __init__(self, manager, env):
		super(Core, self).__init__(manager)

		self.env = env

		if os.name in ["posix", "mac"]:
			signal.signal(signal.SIGHUP, self.onREHASH)
			signal.signal(signal.SIGTERM, self.onTERM)

		# Initialize

		self.running = True
		self.state = State()

	# Service Commands

	@listener("term")
	def onTERM(self, signal=0, stack=0):
		if self.env.bot.connected:
			self.env.bot.ircQUIT("Received SIGTERM, terminating...")
		self.state.set("TERMINATING")

	@listener("rehash")
	def onREHASH(self, signal=0, stack=0):
		self.env.reload()

	@listener("timer:reconnect")
	def onRECONNECT(self, host, port, ssl, bind, auth):
		self.state.set("CONNECTING")
		if bind is not None:
			self.env.bot.open(host, port, ssl, bind)
		else:
			self.env.bot.open(host, port, ssl)

	def run(self):
		env = self.env
		state = self.state
		event = env.event
		timers = env.timers
		bot = env.bot

#		env.loadPlugins()

		host = env.config.get("connect", "host")
		port = env.config.getint("connect", "port")

		auth = {
				"password": env.config.get("connect", "password"),
				"ident": env.config.get("bot", "ident"),
				"nick": env.config.get("bot", "nick"),
				"name": env.config.get("bot", "name"),
				"server": env.config.get("connect", "host"),
				"host": socket.gethostname()
				}

		state.set("CONNECTING")

		if env.config.has_option("connect", "ssl"):
			ssl = env.config.getboolean("connect", "ssl")
		else:
			ssl = False

		if env.config.has_option("connect", "bind"):
			bind = env.config.get("connect", "bind")
		else:
			bind = None

		if bind is not None:
			bot.open(host, port, ssl, bind)
		else:
			bot.open(host, port, ssl)

		while self.running:

			try:
				event.flush()
				timers.poll()
				if bot.connected:
					bot.poll(0.1)
				else:
					sleep(1)

					if state == "TERMINATING":
						self.running = False
					elif not state == "WAITING":
						state.set("DISCONNECTED")

				if state == "CONNECTING":
					if bot.connected:
						state.set("CONNECTED")
				elif state == "CONNECTED":
					state.set("AUTHENTICATED")
					bot.connect(auth)
				elif state == "DISCONNECTED":
					state.set("WAITING")
					env.log.info("Disconnected, reconnecting in 60s...")
					env.timers.add(
							60,
							Reconnect(host, port, ssl, bind, auth),
							"timer:reconnect")
				elif state == "TERMINATING":
					self.running = False
					break
			except UnhandledEvent, evt:
				env.log.warn("Unhandled Event: %s" % evt)
			except KeyboardInterrupt:
				if self.env.bot.connected:
					bot.ircQUIT("Received ^C, terminating...")
				state.set("TERMINATING")
			except Exception, error:
				env.errors += 1
				env.log.error("Error occured: %s" % error)
				env.log.error(format_exc())

		env.unloadPlugins()

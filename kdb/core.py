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
from pprint import pprint
from traceback import format_exc

from pymills.utils import State
from pymills.event import filter, listener, Component

class Core(Component):

	def __init__(self, event, env):
		Component.__init__(self, event)

		self.env = env

		if os.name in ["posix", "mac"]:
			signal.signal(signal.SIGHUP, self.rehash)
			signal.signal(signal.SIGTERM, self.term)

		# Initialize

		self.running = True
		self.state = State()

	# Service Commands

	@listener("term")
	def term(self, signal=0, stack=0):
		if self.env.bot.connected:
			self.env.bot.ircQUIT("Received SIGTERM, terminating...")
		self.state.set("TERMINATING")

	@listener("rehash")
	def rehash(self, signal=0, stack=0):
		self.env.reload()

	@filter()
	def onDEBUG(self, event):
		config = self.env.config
		if config.has_option("logging", "verbose"):
			if config.getboolean("logging", "verbose"):
				self.env.log.debug(event)

	@listener("timer:reconnect")
	def onRECONNECT(self, n, host, port, ssl, bind, auth):
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

		env.loadPlugins()

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
				if bot.connected:
					bot.process()
				else:
					if state == "TERMINATING":
						self.running = False
						break
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
					env.log.info(
							"kdb was disconnected, "
							"Reconnecting in 60s...")
					env.timers.add(
							60,
							channel="timer:reconnect",
							host=host, port=port,
							ssl=ssl, bind=bind, auth=auth)
				elif state == "TERMINATING":
					self.running = False
					break

				timers.process()
				event.flush()
				sleep(0.1)
				if not bot.connected:
					sleep(0.5)
			except KeyboardInterrupt:
				if self.env.bot.connected:
					bot.ircQUIT("Received ^C, terminating...")
				state.set("TERMINATING")
			except Exception, e:
				env.errors += 1
				env.log.error("Error occured: %s" % e)
				env.log.error(format_exc())

		for i in xrange(len(event)):
			event.flush()

		env.unloadPlugins()

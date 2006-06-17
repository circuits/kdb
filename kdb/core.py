# Filename: core.py
# Module:	core
# Date:		2nd August 2005
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id: core.py 251 2006-06-07 14:20:26Z prologic $

"""core

This is the core of kdb.
"""

import os
import signal
import socket

from bot import Bot

class Core:

	def __init__(self, env):
		self.env = env

		if os.name in ["posix", "mac"]:
			signal.signal(signal.SIGHUP, self.rehash)
			signal.signal(signal.SIGTERM, self.term)

		# Initialize

		self.bot = Bot(self.env)

		self.running = True

	# Service Commands

	def term(self, signal=0, stack=0):
		self.stop()
		raise SystemExit, 0
	
	def stop(self):
		self.running = False
	
	def rehash(self, signal=0, stack=0):
		self.env.reload()
	
	def run(self):
		env = self.env
		event = env.event
		timers = env.timers
		bot = self.bot

		bot.open(
				env.config.get("connect", "host"),
				env.config.getint("connect", "port"))

		auth = {
				"password": env.config.get("connect", "password"),
				"ident": env.config.get("bot", "ident"),
				"nick": env.config.get("bot", "nick"),
				"name": env.config.get("bot", "name"),
				"server": env.config.get("connect", "host"),
				"host": socket.gethostname()
				}

		bot.connect(auth)
		bot.joinChannels()

		while self.running:

			if bot.connected:
				bot.process()
			else:
				env.log.info(
						"%s was disconnected, reconnecting..." % (
							bot.getNick(), bot.getServer()))
				bot.open(
						env.config.get("connect", "host"),
						env.config.getint("connect", "port"))
				bot.connect(auth)
				bot.joinChannels()

			timers.run()
			event.flush()

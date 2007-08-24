# Module:	greeting
# Date:		14th July 2007
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Greeting

Displays a greeting for users that join the channel.
Users that have been greeted before will not get further
greetings, unless they haven't been seen for over 3 days.
"""

__ver__ = "0.0.2"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import os
import marshal
from time import time

from pymills.event import listener, Event

from kdb.plugin import BasePlugin

class Irc(BasePlugin):

	"""Greeting plugin

	Displays a greeting for users that join the channel.
	Users that have been greeted before will not get further
	greetings, unless they haven't been seen for over 3 days.

	There are no commands for this plugin.
	"""

	def __init__(self, event, bot, env):
		BasePlugin.__init__(self, event, bot, env)

		self._history = {}

		historyFile = os.path.join(
			self.env.path, "ghist.bin")
		if os.path.exists(historyFile):
			fd = file(historyFile, "rb")
			self._history = marshal.load(fd)
			fd.close()

	def cleanup(self):
		historyFile = os.path.join(
			self.env.path, "ghist.bin")
		fd = file(historyFile, "wb")
		marshal.dump(self._history, fd)
		fd.close()

	@listener("join")
	def onJOIN(self, nick, channel):
		nick = nick.lower()

		if nick == self.bot.getNick().lower():
			return

		if self._history.has_key(nick):
			if (time() - self._history[nick]) > (60*60*24*3):
				msg = "Welcome back %s :)" % nick
				self.bot.ircPRIVMSG(channel, msg)
		else:
			msg = "Hello there %s, Welcome to %s" % (nick, channel)
			self.bot.ircPRIVMSG(channel, msg)

		self._history[nick] = time()

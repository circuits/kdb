# Filename: bot.py
# Module:	bot
# Date:		17th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id: ircbot.py 150 2006-06-11 17:17:55Z prologic $

"""The Bot

...
"""

from pymills.irc import IRC
from pymills.sockets import TCPClient
from pymills.datatypes import CaselessDict

class Bot(TCPClient, IRC):

	def __init__(self, env):
		TCPClient.__init__(self, env.event)
		IRC.__init__(self, env.event)
		self.env = env

#FIXME: One day this should support .eggs and site and local plugins
#		loadPlugins(env)
		self._plugins = CaselessDict()

	def connect(self, auth):

		if auth.has_key("pass"):
			self.ircPASS(auth["password"])

		self.ircUSER(
				auth.get("ident", ""),
				auth.get("host", ""),
				auth.get("server", ""),
				auth.get("name", ""))

		self.ircNICK(auth.get("nick", ""))

	def joinChannels(self):
		self.env.log.debug(
				"channels(config): %s" % 
				self.env.config.get("bot", "channels"))
		channels = [x.strip() for x in 
				self.env.config.get("bot", "channels").split(",")]
		self.env.log.debug("channels: %s" % channels)
		for channel in channels:
			self.ircJOIN(channel)

	def ircRAW(self, data):
		IRC.ircRAW(self, data)
		self.env.log.debug("O: %s" % data)

	def onREAD(self, event):
		IRC.onREAD(self, event)
		self.env.log.debug("I: %s" % event.line)
		return True, event
	onREAD.filter = True

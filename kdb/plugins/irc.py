# Filename: irc.py
# Module:	irc
# Date:		30th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""IRC

This plugin provides various commands to control the
IRC specific features of kdb. eg: Changing it's nickname.
"""

__ver__ = "0.0.7"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from time import sleep

from pymills.event import listener, Event

from kdb.plugin import BasePlugin

class Irc(BasePlugin):

	"""IRC Support plugin

	Provides various general irc commands and support functions.
	eg: NICK, QUIT, etc
	See: commands irc
	"""

	@listener("numeric")
	def onNUMERIC(self, source, target, numeric, arg, message):
		if numeric == 1:
			self.env.event.push(Event(), "connected")
		elif numeric == 433:
			self.env.event.push(Event(), "nicksollision")

	@listener("nick")
	def onNICK(self, source, newnick, ctime):
		if source == self.bot.getNick().lower():
			self.bot.setNick(newnick)

	def cmdJUMP(self, source, server, port=6667, ssl=False):
		"""Connect to another server.
		
		Syntax: JUMP <server> [<port>] [<ssl>]
		"""

		return "Not implemented."

	#	self.bot.ircQUIT("Reconnecting to %s:%s" % (server, port)))
	#	bot.open(host, port, ssl)
	#	sleep(1)
	#	if bot.connected:
	#		bot.connect(auth)

	def cmdQUIT(self, source, message="Bye! Bye!"):
		"""Quit from the current server
		
		Syntax: QUIT [<message>]
		"""

		self.bot.ircQUIT(message)
	
	def cmdDIE(self, source, message="Terminating! Bye!"):
		"""Quit and Terminate
		
		Syntax: DIE [<message>]
		"""

		self.cmdQUIT(source, message)
		self.event.push(Event(), "term")
	
	def cmdJOIN(self, source, channel, key=None):
		"""Join specified channel.
		
		Syntax: JOIN <channel> [<key>]
		"""

		self.bot.ircJOIN(channel, key)

	def cmdNICK(self, source, nick):
		"""Change current nickname
		
		Syntax: NICK <newnick>
		"""

		self.bot.ircNICK(nick)

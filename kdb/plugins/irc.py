# Module:	irc
# Date:		30th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""IRC

This plugin provides various commands to control the
IRC specific features of kdb. eg: Changing it's nickname.
"""

__version__ = "0.0.9"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from time import sleep

from circuits import listener, Event

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
			self.push(Event(), "joinchannels", self.channel)
		elif numeric == 433:
			self.push(Event(), "nicksollision", self.channel)

	def cmdJUMP(self, source, server, port=6667, ssl=False):
		"""Connect to another server.

		Syntax: JUMP <server> [<port>] [<ssl>]
		"""

		return "Not implemented."

	#	self.bot.ircQUIT("Reconnecting to %s:%s" % (server, port)))
	#	bot.open(host, port, ssl)
	#	sleep(1)
	#	if bot.connected:
	#		bot.connect(auth)

	def cmdIRCINFO(self, source):
		"""Display current IRC information such as server,
		network, current nick, etc.

		Syntax: IRCINFO
		"""

		msg = "I am %s on the %s IRC Network connected to " \
				"%s running version %s" % ("%s!%s@%s" % (
					self.bot.getNick(), self.bot.getIdent(),
					self.bot.getHost()),
					self.bot.getNetwork(), self.bot.getServer(),
					self.bot.getServerVersion())

		return msg

	def cmdQUIT(self, source, message="Bye! Bye!"):
		"""Quit from the current server

		Syntax: QUIT [<message>]
		"""

		self.bot.ircQUIT(message)

		return "Left IRC"

	def cmdDIE(self, source, message="Terminating! Bye!"):
		"""Quit and Terminate

		Syntax: DIE [<message>]
		"""

		self.cmdQUIT(source, message)
		self.push(Event(), "stop", "core")

		return "Terminating"

	def cmdNICK(self, source, nick):
		"""Change current nickname

		Syntax: NICK <newnick>
		"""

		self.bot.ircNICK(nick)

		return "Nickname changed to %s" % nick

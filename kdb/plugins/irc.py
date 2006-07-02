# Filename: irc.py
# Module:	irc
# Date:		30th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""IRC

This plugin provides various commands to control the
IRC specific features of kdb. eg: Changing it's nickname.
"""

__ver__ = "0.0.1"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

from pymills.event import Event

from kdb.plugin import BasePlugin

class Irc(BasePlugin):
	"IRC"

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
		self.event.push(
				Event(),
				self.event.getChannelID("term"),
				self)
	
	def cmdNICK(self, source, nick):
		"""Change current nickname
		
		Syntax: NICK <newnick>
		"""

		self.bot.ircNICK(nick)

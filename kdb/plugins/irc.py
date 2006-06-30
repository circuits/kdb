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

from kdb.plugin import BasePlugin

class Irc(BasePlugin):
	"IRC"

	def cmdQUIT(self, source, message="Bye! Bye!"):
		self.bot.ircQUIT(message)
	
	def cmdDIE(self, source, message="Terminating! Bye!"):
		self.cmdQUIT(source, message)
	
	def cmdNICK(self, source, nick):
		self.bot.ircNICK(nick)

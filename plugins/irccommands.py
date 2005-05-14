# Filename: irccommands.py
# Module:   irccommands
# Date:     09th May 2005
# Author:   James Mills <prologic@shortcircuit.net.au>

"""irccommands Plugin

IRC Commands Plugin
"""

__name__ = "irccommands"
__desc__ = "IRC Commands Plugin"
__ver__ = "0.0.1"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

from pymills import ircbot
from pymills.utils import Tokenizer

def init():
	pass

class IRCCommands(ircbot.Plugin):
	"IRCCommands Plugin"

	def __init__(self, bot):
		ircbot.Plugin.__init__(self, bot)

	def getHelp(self, command):

		if command == None:
			help = "Commands: QUIT, DIE, NICK"
		elif command.upper() == "QUIT":
			help = "(Makes me quit this server) - Syntax: QUIT"
		elif command.upper() == "DIE":
			help = "(Makes me terminate) - Syntax: DIE"
		elif command.upper() == "NICK":
			help = "(Changes my nick) - Syntax: NICK <nick>"
		else:
			help = "Invalid Command: %s" % command

		return help

	def doQUIT(self):
		self.bot.stop()

	def doDIE(self):
		self.bot.term()

	def doNICK(self, nick):
		self.bot.ircNICK(nick)

	def onMESSAGE(self, source, target, message):

		(addressed, target, message) = self.isAddressed(source, target, message)

		if addressed:

			tokens = Tokenizer(message)

			if tokens.peek().upper() == "QUIT":
				tokens.next()
				self.doQUIT()
			elif tokens.peek().upper() == "DIE":
				tokens.next()
				self.doDIE()
			elif tokens.peek().upper() == "NICK":
				tokens.next()
				nick = tokens.next()
				self.doNICK(nick)

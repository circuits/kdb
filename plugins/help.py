# Filename: Help.py
# Module:   Help
# Date:     09th May 2005
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Help Plugin

Help Plugin
"""

__name__ = "Help"
__desc__ = "Help Plugin"
__ver__ = "0.0.1"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

from pymills import ircbot
from pymills.utils import Tokenizer

def init():
	pass

class Help(ircbot.Plugin):
	"Help Plugin"

	def __init__(self, bot):
		ircbot.Plugin.__init__(self, bot)

	def getHelp(self, command):

		if command == None:
			help = "Commands: HELP"
		elif command.upper() == "HELP":
			help = "(Display help about some plugin and/or command) - Syntax: HELP <plugin> [<command>]"
		else:
			help = "Invalid Command: %s" % command

		return help

	def doHELP(self, target, plugin, command = None):
		pluginObject = self.bot.getPlugin(plugin)
		if hasattr(pluginObject, "getHelp") and callable(getattr(pluginObject, "getHelp")):
			self.bot.ircPRIVMSG(target, pluginObject.getHelp(command))
		else:
			self.bot.ircPRIVMSG(target, "No help available")

	def onMESSAGE(self, source, target, message):

		(addressed, target, message) = self.isAddressed(source, target, message)

		if addressed:

			tokens = Tokenizer(message)

			if tokens.peek().upper() == "HELP":
				tokens.next()

				if tokens.more():
					plugin = tokens.next()
					command = None
					if tokens.more():
						command = tokens.next()
					self.doHELP(target, plugin, command)
				else:
					self.bot.ircPRIVMSG(target, self.getHelp(None))

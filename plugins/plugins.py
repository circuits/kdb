# Filename: Plugins.py
# Module:   Plugins
# Date:     09th May 2005
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Plugins Plugin

Plugins Plugin
"""

__name__ = "Plugins"
__desc__ = "Plugins Plugin"
__ver__ = "0.0.1"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

import string

from pymills import ircbot
from pymills.utils import Tokenizer

import conf

def init():
	pass

class Plugins(ircbot.Plugin):
	"Plugins Plugin"

	def getHelp(self, command):

		if command == None:
			help = "Commands: LIST INFO"
		elif command.upper() == "LIST":
			help = "(Lists al loaded plugins) - Syntax: LIST"
		elif command.upper() == "INFO":
			help = "(Display info about a plugin) - Syntax: INFO <plugin>"
		else:
			help = "Invalid Command: %s" % command

		return help

	def doLIST(self, target):
		plugins = self.bot.loadedPlugins()
		msg = "Plugins loaded: %s" % string.join(plugins, ", ")
		self.bot.ircPRIVMSG(target, msg)

	def doINFO(self, target, plugin):

		info = self.bot.getPluginInfo(conf.paths["plugins"], plugin)

		if not info == {}:
			name = info["name"]
			ver = info["ver"]
			author = info["author"]
			desc = info["desc"]

			msg = "%s ver %s by %s - %s" % (name, ver, author, desc)
		else:
			msg = "ERROR: Plugin %s not found!" % plugin

		self.bot.ircPRIVMSG(target, msg)

	def onMESSAGE(self, source, target, message):

		(addressed, target, message) = self.isAddressed(source, target, message)

		if addressed:

			tokens = Tokenizer(message)

			if tokens.peek().upper() == "PLUGINS":
				tokens.next()

				if tokens.more():
					if tokens.peek().upper() == "LIST":
						tokens.next()
						self.doLIST(target)
					elif tokens.peek().upper() == "INFO":
						tokens.next()
						plugin = tokens.next()
						self.doINFO(target, plugin)

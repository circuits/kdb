# Filename: Evenets.py
# Module:   Evenets
# Date:     09th May 2005
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Evenets Plugin

Evenets Plugin
"""

__name__ = "Evenets"
__desc__ = "Evenets Plugin"
__ver__ = "0.0.1"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

from pymills import ircbot

def init():
	"""Initialize Function

	This function is called by the Core byefore the plugin is
	loaded. Put any initialization code here>
	"""

	pass

class Evenets(ircbot.Plugin):
	"Evenets Plugin"

	def __init__(self, bot):
		ircbot.Core.Plugin.__init__(self, bot)

	def getHelp(self, command):
		"""Returns a Help String

		This function is used by the Help Plugin to return a
		Help String to the user.
		Write Help Strings for each command here.
		"""

		if command == None:
			help = "Reacts to events, no commands"
		else:
			help = "Invalid Command: %s" % command

		return help

	# Commands
	#
	# Implement any commands and/or functions of your
	# plugins here...

	# Events
	#
	# Implement as many evenets as you need.
	# Removed ones you don't use.

	def onMESSAGE(self, source, target, message):
		pass
	
	def onNOTICE(self, source, target, message):
		pass
	
	def onJOIN(self, source, channel):
		pass

	def onPART(self, source, channel, message):
		pass
	
	def onCTCP(self, source, target, type, message):
		pass
	
	def onNICK(self, source, nick):
		pass
	
	def onMODE(self, nick, modes):
		pass
	
	def onMODE(self, source, channel, modes):
		pass
	
	def onQUIT(self, nick, reason):
		pass
	
	def onTOPIC(self, nick, channel, topic):
		pass
	
	def onINVITE(self, source, to, channel):
		pass
	
	def onKICK(self, source, channel, nick, reason):
		pass

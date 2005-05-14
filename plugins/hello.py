# Filename: Hello.py
# Module:   Hello
# Date:     09th May 2005
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Hello Plugin

Hello Plugin
"""

__name__ = "Hello"
__desc__ = "Hello Plugin"
__ver__ = "0.0.1"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

import random

from pymills import ircbot

greetings = [
	"Bonjour %s",
	"Howdy %s",
	"Hello %s",
	"Hi %s",
	"Greetings %s"
	]

def init():
	pass

def getGreeting():
	return greetings[random.choice(range(0, len(greetings)))]

class Hello(ircbot.Plugin):
	"Hello Plugin"

	def getHelp(self, command):

		if command == None:
			help = "Displays a rangom greeting on persons joining the channel."
		else:
			help = "Invalid Command: %s" % command

		return help

	def onJOIN(self, source, channel):
		if not source[0] == self.bot.getNick():
			self.bot.ircPRIVMSG(channel, getGreeting() % source[0])

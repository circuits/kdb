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

import whrandom
import IRCBot

greetings = [
	"Bonjour %s",
	"Howdy %s",
	"Hello %s",
	"Hi %s",
	"Greetings %s"
	]

def getGreeting():
	global greetings
	ran = whrandom.whrandom()
	num = ran.randint(0, (len(greetings) - 1))
	return greetings[num]

class Hello(IRCBot.Core.Plugin):
	"Hello Plugin"

	def onJOIN(self, source, channel):
		if not source[0] == self.bot.getNick():
			self.bot.ircPRIVMSG(channel, getGreeting() % source[0])

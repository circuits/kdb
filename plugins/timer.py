# Filename: Timer.py
# Module:   Timer
# Date:     09th May 2005
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Timer Plugin

Timer Plugin
"""

__name__ = "Timer"
__desc__ = "Timer Plugin"
__ver__ = "0.0.1"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

from pymills import ircbot
from pymills.utils import Tokenizer

def init():
	pass

class Timer(ircbot.Plugin):
	"Timer Plugin"

	def __init__(self, bot):
		ircbot.Plugin.__init__(self, bot)

	def doSTART(self, target):
		self.bot.timers.add("foo", 5, self.foo, target)
		self.bot.ircPRIVMSG(target, "Timer Started")

	def foo(self, name, length, args):
		target = args[0]
		self.bot.ircPRIVMSG(target, "Timer %s (%d) Executed" % (name, length))

	def onMESSAGE(self, source, target, message):

		(addressed, target, message) = self.isAddressed(source, target, message)

		if addressed:

			tokens = Tokenizer(message)

			if tokens.peek().upper() == "TIMER":
				tokens.next()

				if tokens.peek().upper() == "START":
					tokens.next()
					self.doSTART(target)

# Filename: Stats.py
# Module:   Stats
# Date:     09th May 2005
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Stats Plugin

Stats Plugin
"""

__name__ = "Stats"
__desc__ = "Stats Plugin"
__ver__ = "0.0.2"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

import time

from pymills import ircbot
from pymills.misc import bytes
from pymills.misc import duration
from pymills.utils import Tokenizer

import libkdb

def init():
	pass

class Stats(ircbot.Plugin):
	"Stats Plugin"

	def __init__(self, bot):
		ircbot.Plugin.__init__(self, bot)

		self.startTime = time.time()

	def getHelp(self, command):

		if command == None:
			help = "Commands: UPTIME, NSTATS VERSION"
		elif command.upper() == "UPTIME":
			help = "(Displays current uptime) - Syntax: UPTIME"
		elif command.upper() == "NSTATS":
			help = "(Displays current network stats) - Syntax: NSTATS"
		elif command.upper() == "VERSION":
			help = "(Displays version/build information) - Syntax: VERSION"
		else:
			help = "Invalid Command: %s" % command

		return help

	def doUPTIME(self, target):
		uptime = duration(time.time() - self.startTime)
		cpu = time.clock()
		msg = "Uptime: %s+%s:%s:%s (CPU: %s)" % (uptime + (cpu,))
		self.bot.ircPRIVMSG(target, msg)

	def doNSTATS(self, target):
		traffic = self.bot.getTraffic()

		(in_value, in_postfix) = bytes(traffic[0])
		(out_value, out_postfix) = bytes(traffic[1])
		(total_value, total_postfix) = bytes(traffic[0] + traffic[1])

		in_str = str(in_value) + in_postfix
		out_str = str(out_value) + out_postfix
		total_str = str(total_value) + total_postfix

		msg = "Traffic: (I, O, T) = (%s, %s, %s)" % (in_str, out_str, total_str)

		self.bot.ircPRIVMSG(target, msg)

	def doVERSION(self, target):
		msg = "%s [ %s ] v%s by %s - %s - %s" % (
				libkdb.__name__,
				libkdb.__desc__,
				libkdb.__version__,
				libkdb.__email__,
				libkdb.__copyright__,
				libkdb.__url__)

		self.bot.ircPRIVMSG(target, msg)

	def onMESSAGE(self, source, target, message):

		(addressed, target, message) = self.isAddressed(source, target, message)

		if addressed:

			tokens = Tokenizer(message)

			if tokens.peek().upper() == "UPTIME":
				tokens.next()
				self.doUPTIME(target)
			elif tokens.peek().upper() == "NSTATS":
				tokens.next()
				self.doNSTATS(target)
			elif tokens.peek().upper() == "VERSION":
				tokens.next()
				self.doVERSION(target)

# Filename: Host.py
# Module:   Host
# Date:     09th May 2005
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Host Plugin

Host Plugin
"""

__name__ = "Host"
__desc__ = "Host Plugin"
__ver__ = "0.0.2"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

import socket
import string

from pymills import ircbot
from pymills.utils import Tokenizer

def init():
	pass

class Host(ircbot.Plugin):
	"Host Plugin"

	def __init__(self, bot):
		ircbot.Plugin.__init__(self, bot)

	def getHelp(self, command):

		if command == None:
			help = "Commands: HOST"
		else:
			help = "Invalid Command: %s" % command

		return help

	def doHOST(self, target, host):

		isIP = True
		for c in host.replace(".", ""):
			if not c in string.digits:
				isIP = False
				break

		if isIP:
			try:
				(name, aliases, addresses) = socket.gethostbyaddr(host)
				msg = "%s -> %s" % (host, name)
			except socket.gaierror, e:
				msg = "%s -> %s" % (host, e[1])
			except socket.herror, e:
				msg = "%s -> %s" % (host, e[1])
		else:
			try:
				address = socket.gethostbyname(host)
				msg = "%s -> %s" % (host, address)
			except socket.gaierror, e:
				msg = "%s -> %s" % (host, e[1])

		self.bot.ircPRIVMSG(target, msg)

	def onMESSAGE(self, source, target, message):

		(addressed, target, message) = self.isAddressed(source, target, message)

		if addressed:

			tokens = Tokenizer(message)

			if tokens.peek().upper() == "HOST":
				tokens.next()
				host = tokens.next()
				self.doHOST(target, host)

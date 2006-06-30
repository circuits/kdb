# Filename: bot.py
# Module:	bot
# Date:		17th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id: ircbot.py 150 2006-06-11 17:17:55Z prologic $

"""The Bot

...
"""

from pymills.irc import IRC
from pymills.event import filter, listener
from pymills.sockets import TCPClient

class Bot(TCPClient, IRC):

	def __init__(self, event, env):
		TCPClient.__init__(self)
		IRC.__init__(self)

		self.env = env
	
	def connect(self, auth):

		if auth.has_key("pass"):
			self.ircPASS(auth["password"])

		self.ircUSER(
				auth.get("ident", ""),
				auth.get("host", ""),
				auth.get("server", ""),
				auth.get("name", ""))

		self.ircNICK(auth.get("nick", ""))

	def joinChannels(self):
		channels = [x.strip() for x in 
				self.env.config.get(
					"bot", "channels", "").split(",")
				if not x.strip() == ""]
		self.env.log.debug("Joining channels: %s" % channels)
		for channel in channels:
			self.ircJOIN(channel)

	def ircRAW(self, data):
		self.write(data + "\r\n")

	@filter()
	def onDEBUG(self, event):
		#self.env.log.debug(event)
		return False, event

	@listener("read")
	def onREAD(self, line):
		TCPClient.onREAD(self, line)
		IRC.onREAD(self, line)

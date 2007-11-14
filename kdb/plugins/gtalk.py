# Filename: gtalk.py
# Module:	gtalk
# Date:		30th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Google Talk Plugin

This plugin provides an interface and client to the Google
Talk servers using the XMPP protocol. This plugin enables
communication via Google Talk.

[gtalk]
user = kdb
password = foobar
"""

__ver__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from time import sleep

import xmpp

from pymills.net.irc import MessageEvent
from pymills.event import filter, listener, \
		Event, UnhandledEvent, Worker

from kdb.plugin import BasePlugin

class GTalk(BasePlugin, Worker):

	"""Google Talk Plugin

	This plugin provides an interface and client to the Google
	Talk servers using the XMPP protocol. This plugin enables
	communication via Google Talk.

	See: commands gtalk
	"""

	def __init__(self, event, bot, env):
		BasePlugin.__init__(self, event, bot, env)
		Worker.__init__(self, event)

		self._username = "kdbbot"
		self._password = "semaj2891"
		self._name = "kdb"

		self._client = cnx = xmpp.Client("gmail.com", debug=[])

	def cleanup(self):
		self._client.disconnect()
		self.stop()
	
	def sendMsg(self, to, message):
		self._client.send(xmpp.Message(to, message))

	def run(self):
		while self.isRunning():
			if self._client.isConnected():
				if hasattr(self._client, "Process"):
					self._client.Process()
					sleep(0.01)
				else:
					sleep(1)
			else:
				try:
					self._client.connect(server=("gmail.com", 5223))
				except:
					sleep(60)
				self._client.auth(
						self._username,
						self._password,
						self._name)

				self._client.RegisterHandler(
						"message", self.messageHandler)
				self._client.sendInitPresence()
				sleep(1)
	
	def messageHandler(self, cnx, msg):
		text = msg.getBody()
		user = msg.getFrom()
		self.env.log.debug("<%s> %s" % (user, text))
		if text is not None:
			reply = [x for x in self.send(
				MessageEvent(
					str(user),
					self.bot.getNick(),
					text),
				"message") if x is not None]
			if type(reply) == list:
				if len(reply) > 0:
					if type(reply[0]) == list:
						reply = reply[0] + reply[1:]
				reply = "\n".join(reply)
			self.sendMsg(user, reply)

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

__version__ = "0.2"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from time import sleep

import xmpp

from circuits.lib.irc import Message
from circuits import listener, Event, Worker

from kdb.plugin import BasePlugin

class GTalk(BasePlugin, Worker):

	"""Google Talk Plugin

	This plugin provides an interface and client to the Google
	Talk servers using the XMPP protocol. This plugin enables
	communication via Google Talk.

	See: commands gtalk
	"""

	def __init__(self, env, bot, *args, **kwargs):
		super(GTalk, self).__init__(env, bot, *args, **kwargs)

		self._username = self.env.config.get("gtalk", "username", "kdbbot")
		self._password = self.env.config.get("gtalk", "password", "semaj2891")
		self._name = "kdb"

		self._client = xmpp.Client("gmail.com", debug=[])

		self.start()

	def cleanup(self):
		self._client.disconnect()
		self.stop()
	
	def sendMsg(self, to, message):
		self._client.send(xmpp.Message(to, message))

	def run(self):
		while self.running:
			if self._client.isConnected():
				if hasattr(self._client, "Process"):
					self._client.Process()
					sleep(0.01)
				else:
					sleep(1)
			else:
				try:
					self._client.connect(server=("gmail.com", 5223))
					self._client.auth(
							self._username,
							self._password,
							self._name)
					self._client.RegisterHandler("message", self.messageHandler)
					self._client.sendInitPresence()
				except Exception, error:
					sleep(60)

				sleep(1)

	def messageHandler(self, cnx, message):
		text = message.getBody()
		user = message.getFrom()

		if text is not None:
			self.env.log.debug("<%s> %s" % (user, text))

			if " " in text:
				command, args = text.split(" ", 1)
			else:
				command, text = text, ""

			command = command.upper()

			if command == "SUBSCRIBE":
				self._client.Roster.Authorize(user)
				reply = "Authorized."
			else:
				text = message.getBody()
				e = Message(str(user), self.bot.getNick(), text)
				r = self.iter(e, "message", self.channel)
				reply = "\n".join([x for x in r if x is not None])

			self.sendMsg(user, reply)

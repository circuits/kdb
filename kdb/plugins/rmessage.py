# Filename: rmessage.py
# Module:	rmessage
# Date:		24th September 2007
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""RMessage

This plugin listens for xmlrpc:message events and
sends a MessageEvent into the system and returning
any replies generated.
"""

__ver__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from pymills.net.irc import MessageEvent
from pymills.event import filter, listener, \
		Event, UnhandledEvent, Worker

from kdb.plugin import BasePlugin

class RMessage(BasePlugin):

	"""RMessage plugin

	This doesn't have any user commands available.
	This plugin listens for xmlrpc:message events and
	sends a MessageEvent into the system and returning
	any replies generated.

	Depends on: xmlrpc
	"""

	@listener("xmlrpc:message")
	def onMESSAGE(self, user="anonymous", message=""):

		reply = [x for x in self.send(
			MessageEvent(
				str(user),
				self.bot.getNick(),
				message),
			"message") if x is not None]
		if type(reply) == list:
			if len(reply) > 0:
				if type(reply[0]) == list:
					reply = reply[0] + reply[1:]
			reply = "\n".join(reply)

		return reply.strip()


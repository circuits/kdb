# Module:	rmessage
# Date:		24th September 2007
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""RMessage

This plugin listens for xmlrpc:message events and
sends a MessageEvent into the system and returning
any replies generated.
"""

__ver__ = "0.0.3"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from circuits import listener
from pymills.datatypes import Stack
from circuit.lib.irc import MessageEvent

from kdb.plugin import BasePlugin

class RMessage(BasePlugin):

	"""RMessage plugin

	This doesn't have any user commands available.
	This plugin listens for xmlrpc:message events and
	sends a MessageEvent into the system and returning
	any replies generated.

	Depends on: xmlrpc
	"""

	def __init__(self, *args, **kwargs):
		super(Irc, self).__init__(*args, **kwargs)

		self._rlog = Stack(5)

	def cmdRLOG(self, source):
		"""View Remote Log

		Syntax: RLOG
		"""

		return ["Last 5 remote messages:"] + list(self._rlog)

	@listener("xmlrpc:message")
	def onXMLRPCMESSAGE(self, user="anonymous", message=""):

		self._rlog.push(message)

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

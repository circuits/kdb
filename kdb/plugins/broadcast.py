# Module:	broadcast
# Date:		22th December 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Broadtcasting Support

This plugin provides support for listening to broadcast
messages by listening for a certain pattern of message
and performing some command or event on that.
"""

__version__ = "0.0.2"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from circuits import listener
from circuits.lib.irc import Message

from kdb.plugin import BasePlugin

class Broadcast(BasePlugin):
	"Broadcasting Support"

	def __init__(self, *args, **kwargs):
		super(Broadcast, self).__init__(*args, **kwargs)

		self.prefix = self.env.config.get(
				"broadcast", "prefix") or "@"

	@listener("message")
	def onMESSAGE(self, source, target, message):

		addressed, target, message = self.isAddressed(
				source, target, message)

		if not addressed and len(message) > 0:
			if message[0] == self.prefix:
				self.push(
						Message(source, target,
							"%s, %s" % (
								self.bot.getNick(),
								message[1:])), "message", self.channel)

# Filename: notify.py
# Module:	notify
# Date:		30th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Notify

This plugin listens for xmlrpc:notify events and
displays them on the default xmlrpc channel.
"""

__ver__ = "0.0.2"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from pymills.event import listener

from kdb.plugin import BasePlugin

class Notify(BasePlugin):
	"Notify"

	@listener("xmlrpc:notify")
	def onNOTIFY(self, source="unknown", message=""):

		if self.env.config.has_option("xmlrpc", "channel"):
			channel = self.env.config.get("xmlrpc", "channel")
		else:
			channel = None

		if channel is not None:

			self.bot.ircPRIVMSG(channel,
					"Message from %s:" % source)

			for line in message.split("\n"):
				self.bot.ircPRIVMSG(channel, line)

		return "Message sent to %s" % channel

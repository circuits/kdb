# Filename: ctcp.py
# Module:	ctcp
# Date:		10th September 2007
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""CTCP

This plugin provides responses to IRC CTCP Events and
responds to them appropiately.
"""

__ver__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import time

from pymills.event import listener

import kdb
from kdb.plugin import BasePlugin

class Ctcp(BasePlugin):

	"""IRC CTCP Events Plugin

	This plugin provides responses to IRC CTCP Events and
	responds to them appropiately.

	NOTE: There are no commands for this plugin (yet).
	"""

	@listener("ctcp")
	def onCTCP(self, source, target, type, message):
		"""CTCP Event Handler

		Handle IRC CTCP Events and respond to them
		appropiately.
		"""

		response = None

		if type.lower() == "ping":
			response = ("PING", message)
		elif type.lower() == "time":
			response = ("TIME", time.asctime())
		elif type.lower() == "finger":
			response = ("FINGER",
					"%s - %s" % (
						self.bot.getNick(),
						self.bot.getName()))
		elif type.lower() == "version":
			response = ("VERSION",
					"%s - v%s (%s)" % (
						kdb.__name__,
						kdb.__version__,
						kdb.__url__))

		if response is not None:
			self.bot.ircCTCPREPLY(source, *response)

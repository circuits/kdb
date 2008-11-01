# Module:	seen
# Date:		14th July 2007
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Seen

This plugin provides various functionality to determine
when a particular user was last seen and provides a
command to query the information collected and stored.
"""

__ver__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import marshal
from time import time

from circuits import listener, Event

from kdb.plugin import BasePlugin

class Seen(BasePlugin):

	"""Seen plugin
	This plugin provides various functionality to determine
	when a particular user was last seen and provides a
	command to query the information collected and stored.

	See: commands seen
	"""

	@listener("nick")
	def onNICK(self, nick, newnick, ctime):
		pass

	@listener("join")
	def onJOIN(self, nick, channel):
		pass

	@listener("part")
	def onPART(self, nick, channel, message):
		pass

	@listener("message")
	def onMESSAGE(self, source, target, message):
		pass

	@listener("notice")
	def onNOTICE(self, source, target, message):
		pass

	def cmdSEEN(self, source, nick):
		"""Query and display last seen information for the
		given nick.
		
		Syntax: SEEN <nick>
		"""

		return "Not Implemented"

# Filename: timers.py
# Module:	timers
# Date:		30th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Timers

This plugin shows how to user the timers module.
Provides a test command to create a message to be
display in x seconds.
"""

__ver__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from pymills.event import listener

from kdb.plugin import BasePlugin

class Timers(BasePlugin):
	"Timers"

	@listener("timer")
	def onTIMER(self, name, length, channel, **data):
		if data.has_key("target"):
			if data.has_key("message"):
				target = data["target"]
				message = data["message"]
				self.bot.ircPRIVMSG(target, message)

	def cmdTIMER(self, source, length, message="Hello World"):
		"""Create a new time with the given length and message
		
		Syntax: TIMER <length> [<message>]
		"""

		try:
			length = int(length)
		except ValueError:
			return  "Invalid length specified"

		self.env.timers.add("tesT", length,
				target=source, message=message)
		return "Okay timer set"

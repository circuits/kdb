# Module:	timers
# Date:		30th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Timers

This plugin shows how to user the timers module.
Provides a test command to create a message to be
display in x seconds.
"""

__ver__ = "0.0.2"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from circuits import listener, Event, Timer

from kdb.plugin import BasePlugin

class Message(Event):
	"""Message Event

	args: target, message
	"""

class Timers(BasePlugin):
	"Timers"

	@listener("timer")
	def onTIMER(self, target, message):
		self.bot.ircPRIVMSG(target, message)

	def cmdTIMER(self, source, length, message="Hello World"):
		"""Create a new time with the given length and message
		
		Syntax: TIMER <length> [message]
		"""

		try:
			length = int(length)
		except ValueError:
			return  "Invalid length specified"

		timer = Timer(length, Message(source, message))
		self.manager += timer
		self.env.timers.append(timer)

		return "Okay timer set"

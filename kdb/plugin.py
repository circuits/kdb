# Filename: plugin.py
# Module:	plugin
# Date:		17th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id: ircbot.py 150 2006-06-11 17:17:55Z prologic $

"""Plugin

...
"""

from irc import IRC

class Plugin(IRC):

	def __init__(self, bot, env):
		IRC.__init__(self, env.event)

		self.bot = bot
		self.env = env

		self.__setupEvents__()

	def __setupEvents__(self):
		import inspect

		events = [(x[0][2:].lower(), x[1])
				for x in inspect.getmembers(
					self, lambda x: inspect.ismethod(x) and \
							callable(x) and x.__name__[:2] == "on")]

		for event, handler in events:
			channel = self.env.event.getChannelID(event)
			if channel is None:
				self.env.event.addChannel(event)
				channel = self.env.event.getChannelID(event)
			if getattr(handler, "filter", False):
				self.env.event.addFilter(handler,
				self.env.event.getChannelID(event))
			else:
				self.env.event.addListener(handler,
				self.env.event.getChannelID(event))
	
	def isAddressed(self, source, target, message):
		addressed = False

		if target.lower() == self.bot.getNick().lower():
			addressed = True
		else:
			if len(message) > len(self.bot.getNick()):
				if message[0:len(self.bot.getNick())].lower() \
						== self.bot.getNick().lower():
					addressed = True

		return addressed

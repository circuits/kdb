# Filename: plugin.py
# Module:	plugin
# Date:		17th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id: ircbot.py 150 2006-06-11 17:17:55Z prologic $

"""Plugin

This module provides the basic infastructure for kdb
plugins. Plugins should sub-class BasePlugin.
"""

import inspect

from pymills.misc import backMerge
from pymills.event import Component, filter

class BasePlugin(Component):

	def __init__(self, event, bot, env):
		self.bot = bot
		self.env = env

		self._hooks = {}
		self.__setupCommandHandlers__()

	def __setupCommandHandlers__(self):
		self._handlers = inspect.getmembers(self,
				lambda x: inspect.ismethod(x) and \
						callable(x) and x.__name__[:3] == "cmd")
		for name, handler in self._handlers:
			command = name[3:].lower()
			self._hooks[command] = handler

	@filter("message")
	def onMESSAGE(self, event, source, target, message):

		addressed, target, message = self.isAddressed(
				source, target, message)

		if addressed:
			r = self.processCommand(target, message)
			if r is not None:
				if type(r) == list:
					for line in r:
						self.bot.ircPRIVMSG(target, line)
				else:
					self.bot.ircPRIVMSG(target, r)
				return True, event

		return False, event

	@filter("notice")
	def onNOTICE(self, event, source, target, message):

		addressed, target, message = self.isAddressed(
				source, target, message)

		if addressed:
			r = self.processCommand(target, message)
			if r is not None:
				if type(r) == list:
					for line in r:
						self.bot.ircNOTICE(target, line)
				else:
					self.bot.ircNOTICE(target, r)
				return True, event

		return False, event

	def unknownCommand(self, source, command):
		self.bot.ircNOTICE(source, "Unknown command: %s" % command)

	def syntaxError(self, source, command, message, args):
		self.bot.ircNOTICE(source, "Syntax error (%s): %s" % (
			command, message))
		self.bot.ircNOTICE(source, "Expected: %s" %
				" ".join(args))
	
	def processCommand(self, source, message):
		tokens = message.split(" ")
		command = tokens[0].lower()
		tokens = tokens[1:]

		if command in self._hooks:
			handler = self._hooks[command]
			args, vargs, kwargs, default = inspect.getargspec(
					handler)
			args.remove("self")
			args.remove("source")

			if len(args) == len(tokens):
				if len(args) == 0:
					return handler(source)
				else:
					return handler(source, *tokens)
			else:
				if len(tokens) > len(args):
					if vargs is None:
						if len(args) > 0:
							factor = len(tokens) - len(args) + 1
							return handler(source, *backMerge(tokens, factor))
						else:
							self.syntaxError(
									source, command, tokens,
									[x for x in args + [vargs]
										if x is not None])
					else:
						return handler(source, *tokens)
				elif default is not None and len(args) == (
						len(tokens) + len(default)):
					return handler(source, *(tokens + list(default)))
				else:
					self.syntaxError(
							source, command, tokens,
							[x for x in args + [vargs]
								if x is not None])

	def isAddressed(self, source, target, message):
		addressed = False

		if target.lower() == self.bot.getNick().lower():
			if len(message) > len(self.bot.getNick()) and \
					message[0:len(self.bot.getNick())].lower() \
					== self.bot.getNick().lower():
				message = message[len(self.bot.getNick()):]
				while len(message) > 0 and message[0] in [
						",", ":", " "]:
					message = message[1:]

			return True, source, message
		else:
			if len(message) > len(self.bot.getNick()) and \
					message[0:len(self.bot.getNick())].lower() \
					== self.bot.getNick().lower():

				message = message[len(self.bot.getNick()):]
				while len(message) > 0 and message[0] in [
						",", ":", " "]:
					message = message[1:]

				return True, target, message
			else:
				return False, target, message

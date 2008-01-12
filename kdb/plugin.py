# Filename: plugin.py
# Module:	plugin
# Date:		17th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Plugin

This module provides the basic infastructure for kdb
plugins. Plugins should sub-class BasePlugin.
"""

import inspect

from pymills.misc import backMerge
from pymills.event import Component, filter, FilterEvent

class BasePlugin(Component):

	def __init__(self, event, bot, env):
		Component.__init__(self, event)

		self.bot = bot
		self.env = env

		self._hooks = {}
		self.__setupCommandHandlers__()

	def __setupCommandHandlers__(self):
		self._cmdHandlers = inspect.getmembers(self,
				lambda x: inspect.ismethod(x) and \
						callable(x) and x.__name__[:3] == "cmd")
		for name, cmdHandler in self._cmdHandlers:
			command = name[3:].lower()
			self._hooks[command] = cmdHandler

	@filter("message")
	def onMESSAGE(self, event, source, target, message):

		addressed, target, message = self.isAddressed(
				source, target, message)

		if addressed:
			r = self.processCommand(target, message)
			if r is not None:
				if type(target) == tuple:
					target = target[0]
				if type(r) == list:
					for line in r:
						self.bot.ircPRIVMSG(target, line)
				else:
					self.bot.ircPRIVMSG(target, r)

				try:
					raise FilterEvent
				finally:
					return r

	@filter("notice")
	def onNOTICE(self, event, source, target, message):

		addressed, target, message = self.isAddressed(
				source, target, message)

		if addressed:
			r = self.processCommand(target, message)
			if r is not None:
				if type(target) == tuple:
					target = target[0]
				if type(r) == list:
					for line in r:
						self.bot.ircNOTICE(target, line)
				else:
					self.bot.ircNOTICE(target, r)

				try:
					raise FilterEvent
				finally:
					return r

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
			cmdHandler = self._hooks[command]
			args, vargs, kwargs, default = inspect.getargspec(
					cmdHandler)
			args.remove("self")
			args.remove("source")

			if len(args) == len(tokens):
				if len(args) == 0:
					return cmdHandler(source)
				else:
					return cmdHandler(source, *tokens)
			else:
				if len(tokens) > len(args):
					if vargs is None:
						if len(args) > 0:
							factor = len(tokens) - len(args) + 1
							return cmdHandler(source, *backMerge(tokens, factor))
						else:
							self.syntaxError(
									source, command, tokens,
									[x for x in args + [vargs]
										if x is not None])
					else:
						return cmdHandler(source, *tokens)
				elif default is not None and len(args) == (
						len(tokens) + len(default)):
					return cmdHandler(source, *(tokens + list(default)))
				else:
					self.syntaxError(
							source, command, tokens,
							[x for x in args + [vargs]
								if x is not None])

	def isAddressed(self, source, target, message):
		addressed = False

		if self.bot.getNick() is None:
			return False, target, message

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

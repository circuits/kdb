# Module:	plugin
# Date:		17th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""plugin - Base Plugin

This module provides the basic infastructure for kdb
plugins. Plugins should sub-class BasePlugin.
"""

import re
import inspect

from circuits import listener, Event, Component

from pymills.misc import backMerge

###
### Events
###

class Command(Event):
	"""Command(Event) -> Command Event

	args: command, tokens
	"""

###
### Helper Classes
###

class CommandHandler(object):

	def __init__(self, parent):
		self.parent = parent

	def syntaxError(self, source, command, message, args):
		return [
				"Syntax error (%s): %s" % (command, message),
				"Expected: %s" % " ".join(args)]

	def __call__(self, command, source, *args, **kwargs):

		cmdHandler = "cmd%s" % command.upper()
		if hasattr(self, cmdHandler):
			f = getattr(self, cmdHandler)
			if callable(f):
				fargs, fvargs, fkwargs, fdefault = \
						inspect.getargspec(f)
				fargs.remove("self")
				fargs.remove("source")

				if len(fargs) == len(args):
					if len(fargs) == 0:
						return f(source)
					else:
						return f(source, *args)
				else:
					if len(args) > len(fargs):
						if fvargs is None:
							if len(fargs) > 0:
								factor = len(args) - len(fargs) + 1
								return f(source, *backMerge(args, factor))
							else:
								return self.syntaxError(
										source, command, args,
										[x for x in fargs + [fvargs]
											if x is not None])
						else:
							return f(source, *args)
					elif fdefault is not None and len(fargs) == (
							len(args) + len(fdefault)):
						return f(source,
								*(args + list(fdefault)))
					else:
						return self.syntaxError(
								source, command, args,
								[x for x in fargs + [fvargs]
									if x is not None])

		return "Unknown command: %s" % command

###
### Components
###

class BasePlugin(Component):

	channel = "bot"

	def __init__(self, env, bot, *args, **kwargs):
		super(BasePlugin, self).__init__(*args, **kwargs)

		self.env = env
		self.bot = bot

		self._hooks = {}
		self.__setupCommandHandlers__()

	def __setupCommandHandlers__(self):
		self._cmdHandlers = inspect.getmembers(self,
				lambda x: inspect.ismethod(x) and \
						callable(x) and x.__name__[:3] == "cmd")
		for name, cmdHandler in self._cmdHandlers:
			command = name[3:].lower()
			self._hooks[command] = cmdHandler

	@listener("message", type="filter")
	def onMESSAGE(self, source, target, message):

		addressed, target, message = self.isAddressed(
				source, target, message)

		if addressed:
			r = self.processCommand(target, message)
			if r is not None:
				if re.match(".*@.*\/", source):
					return r
				else:
					if type(target) == tuple:
						target = target[0]
					if type(r) == list:
						for line in r:
							self.bot.ircPRIVMSG(target, line)
					else:
						self.bot.ircPRIVMSG(target, r)

	@listener("notice", type="filter")
	def onNOTICE(self, source, target, message):

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

		r = None

		if command in self._hooks:
			cmdHandler = self._hooks[command]
			args, vargs, kwargs, default = inspect.getargspec(
					cmdHandler)
			args.remove("self")
			args.remove("source")

			if len(args) == len(tokens):
				if len(args) == 0:
					r =  cmdHandler(source)
				else:
					r =  cmdHandler(source, *tokens)
			else:
				if len(tokens) > len(args):
					if vargs is None:
						if len(args) > 0:
							factor = len(tokens) - len(args) + 1
							r =  cmdHandler(source, *backMerge(tokens, factor))
						else:
							self.syntaxError(
									source, command, tokens,
									[x for x in args + [vargs]
										if x is not None])
					else:
						r =  cmdHandler(source, *tokens)
				elif default is not None and len(args) == (
						len(tokens) + len(default)):
					r =  cmdHandler(source, *(tokens + list(default)))
				else:
					self.syntaxError(
							source, command, tokens,
							[x for x in args + [vargs]
								if x is not None])

		if r:
			self.push(Command(command, tokens), "PostCommand")

		return r

	def isAddressed(self, source, target, message):
		addressed = False

		if self.bot.getNick() is None:
			return False, target, message

		if target.lower() == self.bot.getNick().lower():
			if len(message) > len(self.bot.getNick()) and \
					message[:len(self.bot.getNick())].lower() \
					== self.bot.getNick().lower():
				message = message[len(self.bot.getNick()):]
				while len(message) > 0 and message[0] in [
						",", ":", " "]:
					message = message[1:]

			return True, source, message
		else:
			if len(message) > len(self.bot.getNick()) and \
					message[:len(self.bot.getNick())].lower() \
					== self.bot.getNick().lower():

				message = message[len(self.bot.getNick()):]
				while len(message) > 0 and message[0] in [
						",", ":", " "]:
					message = message[1:]

				return True, target, message
			else:
				return False, target, message

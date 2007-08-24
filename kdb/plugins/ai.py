# Filename: ai.py
# Module:	ai
# Date:		30th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Artificial Intelligence

This plugin uses the PyAIML library to implement
a somewhat crude artificial intelligence that can
respond to users.
"""

__ver__ = "0.0.2"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


import os
import marshal

import aiml

from pymills.event import listener

from kdb.plugin import BasePlugin

class Ai(BasePlugin):
	"Artificial Intelligence"

	def __init__(self, event, bot, env):
		BasePlugin.__init__(self, event, bot, env)

		self.k = aiml.Kernel()

		self.k.verbose(False)

		self.k.setPredicate("secure", "yes")
		cwd = os.getcwd()
		os.chdir(os.path.join(self.env.path, "aiml"))
		self.k.bootstrap(
				learnFiles="kdb.xml",
				commands="bootstrap")
		self.k.setPredicate("secure", "no")
		os.chdir(cwd)

		if self.env.config.has_section("aiml"):
			for name, value in self.env.config.items("aiml"):
				self.k.setBotPredicate(name, value)

		sessionFile = os.path.join(
			self.env.path, "aiml", "all.ses")
		if os.path.exists(sessionFile):
			fd = file(sessionFile, "rb")
			sessions = marshal.load(fd)
			fd.close()
			for session in sessions.keys():
				for pred,value in sessions[session].items():
					self.k.setPredicate(pred, value, session)

		self.enabled = True

	def cleanup(self):
		session = self.k.getSessionData()
		sessionFile = os.path.join(
			self.env.path, "aiml", "all.ses")
		fd = file(sessionFile, "wb")
		marshal.dump(session, fd)
		fd.close()

	def cmdPUBAI(self, source, option):
		"""Turn public AI on or off.
		
		Syntax: PUBAI ON|OFF
		"""

		opt = option.upper()
		if opt == "ON":
			if not self.enabled:
				self.enabled = True
				msg = "Public AI turned on."
			else:
				msg = "Public AI already on."
		elif opt == "OFF":
			if self.enabled:
				self.enabled = False
				msg = "Public AI turned off."
			else:
				msg = "Public AI not on."
		else:
			msg = "Unknown options: %s" % option

		return msg
	
	@listener("message")
	def onMESSAGE(self, source, target, message):

		addressed, target, message = self.isAddressed(
				source, target, message)

		if addressed or self.enabled:

			if type(target) == tuple:
				target = target[0]

			reply = self.k.respond(message, source)

			self.env.log.debug("AI Reply: %s" % reply)

			if reply:
				for sentence in reply.split("\n\n"):
					self.bot.ircPRIVMSG(target, sentence)

	@listener("notice")
	def onNOTICE(self, source, target, message):

		addressed, target, message = self.isAddressed(
				source, target, message)

		if addressed or self.enabled:

			if type(target) == tuple:
				target = target[0]

			reply = self.k.respond(message, source)

			if reply:
				for sentence in reply.split("\n\n"):
					self.bot.ircNOTICE(target, sentence)

# Filename: ai.py
# Module:	ai
# Date:		30th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Artificial Intelligence

This plugin uses the PyAIML library to implement
a somewhat crude artificial intelligence that can
respond to users.
"""

__ver__ = "0.0.1"
__author__ = "James Mills <prologic@shortcircuit.net.au>"


import os
import aiml

from pymills.event import filter

from kdb.plugin import BasePlugin

class Ai(BasePlugin):
	"Artificial Intelligence"

	def __init__(self, event, bot, env):
		BasePlugin.__init__(self, event, bot, env)

		self.k = aiml.Kernel()
		self.k.bootstrap(
				learnFiles=os.path.join(
					self.env.path, "aiml", "kdb.xml"),
				commands="load aiml b")

		if self.env.config.has_section("aiml"):
			for name, value in self.env.config.items("aiml"):
				self.k.setBotPredicate(name, value)

		sessionFile = os.path.join(
			self.env.path, "aiml", "all.ses")
		if os.path.exists(sessionFile):
			fp = file(sessionFile, "rb")
			sessions = marshal.load(fp)
			sessionFile.close()
			for session in sessions.keys():
				for pred,value in sessions[session].items():
					self.k.setPredicate(pred, value, session)

		self.enabled = True

	def __del__(self):
		session = self.k.getSessionData()
		sessionFile = os.path.join(
			self.env.path, "aiml", "all.ses")
		fp = file(sessionFile, "wb")
		marshal.dump(session, fp)
		sessionFile.close()

	def cmdAI(self, source, option):

		opt = option.upper()
		if opt == "ON":
			if not self.enabled:
				self.enabled = True
				msg = "Public AIML turned on."
			else:
				msg = "Public AIML already on."
		elif opt == "OFF":
			if self.enabled:
				self.enabled = True
				msg = "Public AIML turned off."
			else:
				msg = "Public AIML not on."
		else:
			msg = "Unknown options: %s" % option

		return msg
	
	@filter("message")
	def onMESSAGE(self, event, source, target, message):

		addressed, target, message = self.isAddressed(
				source, target, message)

		if addressed or self.enabled:

			reply = self.k.respond(message, source)

			if reply:
				for sentence in reply.split("\n\n"):
					self.bot.ircPRIVMSG(target, sentence)
				return True, event

		return False, event

	@filter("notice")
	def onNOTICE(self, event, source, target, message):

		addressed, target, message = self.isAddressed(
				source, target, message)

		if addressed or self.enabled:

			reply = self.k.respond(message, source)

			if reply:
				for sentence in reply.split("\n\n"):
					self.bot.ircNOTICE(target, sentence)
				return True, event

		return False, event

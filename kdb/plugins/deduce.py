# Filename: deduce.py
# Module:	deduce
# Date:		03th July 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Deductive Logic

This plugin implements a simple deductive logic which
allows the user to define facts and ask questions about it.
"""

__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import os
import re

from circuits import listener
from pymills.ai.deduce import fact, brain

from kdb.plugin import BasePlugin

class Deduce(BasePlugin):
	"Deductive Logic"

	def __init__(self, *args, **kwargs):
		super(Deduce, self).__init__(*args, **kwargs)

		self.reason = []
		self.b = brain()

		filename = os.path.join(self.env.path, "deduce.bin")
		if os.path.exists(filename):
			fp = open(filename, "r")
			for i, line in enumerate(fp):
				line = line.strip()
				msg, self.reason = self.b.learn(line)
				self.env.log.debug(
						"%d: %s (%s)" % (i, line, msg))
			fp.close()

	def cleanup(self):
		filename = os.path.join(self.env.path, "deduce.bin")
		fp = open(filename, "w")
		fp.write(str(self.b))
		fp.close()

	@listener("message")
	def onMMESSAGE(self, source, target, message):

		addressed, target, message = self.isAddressed(
				source, target, message)

		if addressed:

			if type(target) == tuple:
				target = target[0]

			if re.match(" *why ?\??(?i)", message):
				if len(self.reason) == 0:
					msg = "*shrugs*"
				elif len(self.reason) == 1:
					if (self.reason[0].subj == self.reason[0].obj):
						if (self.reason[0].negative == 0):
							msg = "What else would %s %s be ?" % (
									self.reason[0].subj_adj,
									self.reason[0].subj)
						else:
							msg = "%s %s %s" % (
									self.reason[0].subj,
									self.reason[0].orig_verb,
									self.reason[0].ob)
					else:
						msg = "Someone said earlier that %s" % \
								self.reason[0].swap_person()
				else:
					msg = ["Because:"] + \
							[" %s" % r.swap_person()
									for r in self.reason]

				if type(msg) == list:
					for line in msg:
						self.bot.ircPRIVMSG(target, line)
				else:
						self.bot.ircPRIVMSG(target, msg)
				return msg

			message = message.strip()

			self.env.log.debug(message)

			f = fact(message)

			if f.question == 0:
				self.env.log.debug("Learning: %s" % message)
				msg, self.reason = self.b.learn(message)
			else:
				self.env.log.debug("Querying: %s" % message)
				ans, msg, self.reason = self.b.query(message)
				self.env.log.debug(ans)
				self.env.log.debug(msg)

			self.bot.ircPRIVMSG(target, msg)

			return msg

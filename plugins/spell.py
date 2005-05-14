# Filename: Spell.py
# Module:   Spell
# Date:     09th May 2005
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Spell Plugin

Spell Plugin
"""

__name__ = "Spell"
__desc__ = "Spell Plugin"
__ver__ = "0.0.1"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

import string
import enchant

from pymills import ircbot
from pymills.utils import Tokenizer

defaultLanguage = "en_US"

def init():
	pass

class Spell(ircbot.Plugin):
	"Spell Plugin"

	def __init__(self, bot):
		ircbot.Plugin.__init__(self, bot)

		self.language = defaultLanguage
		self.d = d = enchant.request_dict(self.language)

	def getHelp(self, command):

		if command == None:
			help = "(Check spelling of a given word) - Syntax: SPELL <word>"

		return help

	def doSPELL(self, target, word):
		
		if self.d.check(word):
			msg = "%s is spelled correctly." % word
		else:
			suggestions = self.d.suggest(word)
			msg = "%s ? Try -> %s" % (word, string.join(suggestions, ", "))

		self.bot.ircPRIVMSG(target, msg)

	def onMESSAGE(self, source, target, message):

		(addressed, target, message) = self.isAddressed(source, target, message)

		if addressed:

			tokens = Tokenizer(message)

			if tokens.peek().upper() == "SPELL":

				tokens.next()
				word = tokens.next()
				self.doSPELL(target, word)

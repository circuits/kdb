# Filename: spell.py
# Module:	spell
# Date:		30th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Spell Checker

This plugin provides to the user a command that
can be used to check the spelling of words and
give suggestions for incorrectly spelled words.
"""

__ver__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import enchant

from kdb.plugin import BasePlugin

DEFAULT_LANGUAGE = "en_US"

class Spell(BasePlugin):
	"Spell Checker"

	def __init__(self, event, bot, env):
		BasePlugin.__init__(self, event, bot, env)

		self.language = DEFAULT_LANGUAGE
		self.d = d = enchant.request_dict(self.language)

	def cmdSPELL(self, source, word):
		"""Check the spelling of the given word
		
		Syntax: SPELL <word>
		"""

		if self.d.check(word):
			msg = "%s is spelled correctly." % word
		else:
			suggestions = self.d.suggest(word)
			msg = "%s ? Try -> %s" % (
					word, ", ".join(suggestions))

		return msg

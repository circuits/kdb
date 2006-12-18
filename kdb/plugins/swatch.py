# Filename: swatch.py
# Module:	swatch
# Date:		19th December 2006
# Author:	James Mills prologic at shortcircuit dot net dot au

"""Swatch Time

This plugin provides to the user a command that
can be used to display the current Swatch Time or
Internet Time or Beat.
"""

__ver__ = "0.0.1"
__author__ = "James Mills prologic at shortcircuit dot net dot au"

from pymills.misc import beat

from kdb.plugin import BasePlugin

class Swatch(BasePlugin):
	"Swatch Time"

	def __init__(self, event, bot, env):
		BasePlugin.__init__(self, event, bot, env)

	def cmdBEAT(self, source):
		"""Display the current Swatch Time (Internet Time)
		
		Syntax: BEAT
		"""

		return "@%0.2f" % beat()

	def cmdITIME(self, source, name):
		"""Synonym, of BEAT
		
		See: BEAT
		"""

		return self.cmdBEAT(source)

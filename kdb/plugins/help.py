# Filename: help.py
# Module:	help
# Date:		30th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Help Messages

This plugin allows the user to get help for command
of other plugins. It retrieves the __doc__ of the
specified command.
"""

__ver__ = "0.0.1"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

import inspect

from kdb.plugin import BasePlugin

class Help(BasePlugin):
	"Help Message"

	def cmdHELP(self, source, command=None):
		"""Display help for the given command.
		
		Syntax: HELP <command>
		"""

		msg = None

		if command == None:
			command = "help"

		cmd = command.upper()
		for plugin in self.env.plugins.values():
			if hasattr(plugin, "cmd%s" % cmd):
				msg = getattr(
						getattr(plugin, "cmd%s" % cmd),
						"__doc__")
				if msg is None:
					msg = ["No help available for '%s'" % command]
				else:
					msg = msg.split("\n")

		if msg is None:
			msg = ["ERROR: Can't find help for '%s'" % command]

		return msg

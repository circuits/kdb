# Filename: help.py
# Module:	help
# Date:		30th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Help Messages

This plugin allows the user to get help for command
of other plugins. It retrieves the __doc__ of the
specified command.
"""

__ver__ = "0.0.2"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import inspect

from kdb.plugin import BasePlugin

class Help(BasePlugin):
	"Help Message"

	def cmdCOMMANDS(self, source, plugin=None):
		"""Display a list of commands for 'plugin'.
		
		Syntax: COMMANDS <plugin>
		"""

		msg = None

		if plugin == None:
			plugin = "help"

		if self.env.plugins.has_key(plugin.lower()):
			o = self.env.plugins[plugin.lower()]
			commands = [x[0][3:].lower() for x in inspect.getmembers(
				o, lambda x: inspect.ismethod(x) and
				callable(x) and x.__name__.startswith("cmd"))]

			msg = "Available commands for %s: %s" % (
				plugin, " ".join(commands))

		if msg is None:
			msg = ["ERROR: Plugin mis-match or not loaded."]

		return msg

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
						"__doc__") or \
								"No help available for '%s'" % command
				msg = msg.strip()
				msg = msg.replace("\t\t", "\t")
				msg = msg.replace("\t", "   ")
				msg = msg.split("\n")

		if msg is None:
			msg = ["ERROR: Can't find help for '%s'" % command]

		return msg

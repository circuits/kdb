# Filename: help.py
# Module:	help
# Date:		30th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Help Messages

This plugin allows the user to get help for command
of other plugins. It retrieves the __doc__ of the
specified command.
"""

__ver__ = "0.0.4"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import inspect

from kdb.plugin import BasePlugin

class Help(BasePlugin):

	"""Help plugin

	Provides commands to display helpful infomration about
	other plugins and their commands.
	See: commands help
	"""

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

	def cmdHELP(self, source, s=None):
		"""Display help for the given command or plugin.
		
		Syntax: HELP <s>
		"""

		msg = None

		if s == None:
			s = "help"

		sl = s.lower()
		su = s.upper()

		if sl in self.env.plugins:
			msg = self.env.plugins[sl].__doc__
		else:
			for plugin in self.env.plugins.values():
				if hasattr(plugin, "cmd%s" % su):
					msg = getattr(
							getattr(plugin, "cmd%s" % su),
							"__doc__") or \
									"No help available for '%s'" % s

		msg = msg.strip()
		msg = msg.replace("\t\t", "\t")
		msg = msg.replace("\t", "   ")
		msg = msg.split("\n")

		if msg is None:
			msg = ["ERROR: Can't find help for '%s'" % s]

		return msg

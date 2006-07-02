# Filename: core.py
# Module:	core
# Date:		09th May 2005
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Core and Plugin Management

This plugin allows the user to manage other plugins and
kdb's core. You can load/unload plugins on the fly and
rehash kdb forcing it to re-load it's environment.
"""

__ver__ = "0.0.2"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

from kdb.plugin import BasePlugin

class Core(BasePlugin):
	"Core and Plugin Management"

	def cmdREHASH(self, source):
		"""Reload environment
		
		Syntax: RELOAD
		"""

		self.env.reload()
		msg = "Environment reloaded"
		return msg

	def cmdPLUGINS(self, source):
		"""List loaded plugins
		
		Syntax: PLUGINS
		"""

		plugins = self.env.plugins.keys()
		msg = "Plugins loaded: %s" % ", ".join(plugins)
		return msg
	
	def cmdLOAD(self, source, plugin):
		"""Load a plugin
		
		Syntax: LOAD <plugin>
		"""

		if self.env.loadPlugin(self.bot, plugin):
			msg = "Plugin '%s' loaded" % plugin
		else:
			msg = "Error while loading plugin '%s' (See log)" % plugin
		return msg

	def cmdRELOAD(self, source, plugin):
		"""Reload an already loaded plugin
		
		Syntax: RELOAD <plugin>
		"""

		if not plugin in self.env.plugins:
			msg = "ERROR: Plugin '%s' is not loaded" % plugin

		self.env.unloadPlugin(plugin)
		self.env.loadPlugin(self.bot, plugin)

		msg = "Plugin '%s' reloaded" % plugin

		return msg

	def cmdUNLOAD(self, source, plugin):
		"""Unload an already loaded plugin
		
		Note: You cannot unload the "core" plugin.
		
		Syntax: UNLOAD <plugin>
		"""

		if plugin == "core":
			return "ERROR: Unloading the core plugin is disallowed."

		if plugin in self.env.plugins:
			self.env.unloadPlugin(plugin)
			msg = "Plugin '%s' unloaded" % plugin
		else:
			msg = "ERROR: Plugin '%s' is not loaded" % plugin
		return msg

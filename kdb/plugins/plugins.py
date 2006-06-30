# Filename: plugins.py
# Module:	plugins
# Date:		09th May 2005
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Plugin Management

This plugin allows the user to manage other plugins.
You can load/unload plugins on the fly.
"""

__ver__ = "0.0.1"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

from kdb.plugin import BasePlugin

class Plugins(BasePlugin):
	"Plugin Management"

	def cmdLIST(self, source):
		plugins = self.env.plugins.keys()
		msg = "Plugins loaded: %s" % ", ".join(plugins)
		self.bot.ircPRIVMSG(source, msg)
	
	def cmdLOAD(self, source, plugin):
		if self.env.loadPlugin(self.bot, plugin):
			msg = "Plugin '%s' loaded" % plugin
		else:
			msg = "Error while loading plugin '%s' (See log)" % plugin
		self.bot.ircPRIVMSG(source, msg)

	def cmdRELOAD(self, source, plugin):
		if not plugin in self.env.plugins:
			msg = "ERROR: Plugin '%s' is not loaded" % plugin

		self.env.unloadPlugin(plugin)
		self.env.loadPlugin(self.bot, plugin)

		msg = "Plugin '%s' reloaded" % plugin

		self.bot.ircPRIVMSG(source, msg)

	def cmdUNLOAD(self, source, plugin):
		if plugin in self.env.plugins:
			self.env.unloadPlugin(plugin)
			msg = "Plugin '%s' unloaded" % plugin
		else:
			msg = "ERROR: Plugin '%s' is not loaded" % plugin
		self.bot.ircPRIVMSG(source, msg)

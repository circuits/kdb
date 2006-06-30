# Filename: env.py
# Module:	env
# Date:		15 June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id: __init__.py 202 2006-05-26 18:58:45Z prologic $

"""Environment Container

...
"""

from pymills.env import BaseEnvironment
from pymills.utils import safe__import__

from kdb import default_config

VERSION = 1

class Environment(BaseEnvironment):

	def __init__(self, path, create=False):
		"initializes x; see x.__class__.__doc__ for signature"

		import kdb
		from kdb import default_db

		BaseEnvironment.__init__(self,
				path,
				kdb.__name__,
				VERSION,
				default_config.CONFIG,
				(default_db.TABLES, default_db.DATA),
				kdb.__url__,
				create)

		from pymills.timers import Timers
		from pymills.event import EventManager

		self.event = EventManager()
		self.timers = Timers(self.event)

	def create(self):
		BaseEnvironment.create(self)

		import os
		os.mkdir(os.path.join(self.path, "plugins"))
	
	def loadPlugin(self, bot, plugin):
		"""E.loadPlugin(bot, plugin) -> None

		Load a single plugin given by plugin.
		If this plugin is already laoded, it'll be
		replaced.
		"""

		import sys
		from traceback import format_exc

		from kdb.plugin import BasePlugin

		try:
			fqplugin = "kdb.plugins.%s" % plugin
			if sys.modules.has_key(fqplugin):
				self.log.debug("Reloading plugin: %s" % plugin)
				try:
					reload(sys.modules[fqplugin])
					self.log.debug("Reloaded plugin: %s" % plugin)
				except Exception, e:
					self.log.error("Error loading plugin '%s': %s" % (
						plugin, e))
					self.log.error(format_exc())
					return False
			m = safe__import__("plugins.%s" % plugin,
					globals(), locals(), "kdb")
			if hasattr(m, plugin.capitalize()):
				c = getattr(m, plugin.capitalize())
				if issubclass(c, BasePlugin):
					self.plugins[plugin] = c(
							self.event, bot, self)
			self.log.debug("Loaded plugin: %s" % plugin)
			return True
		except Exception, e:
			self.log.error("Error loading plugin '%s': %s" % (
				plugin, e))
			self.log.error(format_exc())
			return False

	def unloadPlugin(self, plugin):
		"""E.unloadPlugin(plugin) -> None

		Unload the specified plugin if it has been loaded.
		"""

		if self.plugins.has_key(plugin):
			self.log.debug("Unloaded plugin: %s" % plugin)
			o = self.plugins[plugin]
			o.unregister()
			del o
			del self.plugins[plugin]
		
	def loadPlugins(self, bot):
		"""E.loadPlugins(bot) -> None

		Load any available plugins loading the global/default
		ones first, then loading the ones found in the
		environment. Plugins found in the environment
		may override existing plugins already loaded.
		"""

		self.plugins = {}
		plugins = default_config.DEFAULT_PLUGINS
		self.log.debug(
				"Loading default plugins: %s" % str(plugins))

		for plugin in plugins:
			self.log.debug("Loading plugin: %s" % plugin)
			self.loadPlugin(bot, plugin)
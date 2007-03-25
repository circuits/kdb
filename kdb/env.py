# Filename: env.py
# Module:	env
# Date:		15 June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Environment Container

...
"""

import os
import sys
import inspect
from traceback import format_exc

from pymills.timers import Timers
from pymills.event import EventManager
from pymills.env import BaseEnvironment
from pymills.utils import safe__import__

import kdb
from kdb.bot import Bot
from kdb import default_db
from kdb import default_config
from kdb.plugin import BasePlugin

VERSION = 1

class Environment(BaseEnvironment):

	def __init__(self, path, create=False):
		"initializes x; see x.__class__.__doc__ for signature"


		BaseEnvironment.__init__(self,
				path,
				kdb.__name__,
				VERSION,
				default_config.CONFIG,
				(default_db.TABLES, default_db.DATA),
				kdb.__url__,
				create)

		self.event = EventManager()
		self.timers = Timers(self.event)

		self.bot = Bot(self.event, self)
		self.loadPlugins()

		self.errors = 0

	def create(self):
		BaseEnvironment.create(self)

		os.mkdir(os.path.join(self.path, "plugins"))
	
	def loadPlugin(self, plugin):
		"""E.loadPlugin(plugin) -> None

		Load a single plugin given by plugin.
		If this plugin is already laoded, it'll be
		replaced.
		"""

		try:
			fqplugin = "kdb.plugins.%s" % plugin
			if sys.modules.has_key(fqplugin):
				try:
					reload(sys.modules[fqplugin])
				except Exception, e:
					self.log.error("Error loading plugin '%s': %s" % (
						plugin, e))
					self.log.error(format_exc())
					return False

			m = safe__import__("plugins.%s" % plugin,
					globals(), locals(), "kdb")

			classes = inspect.getmembers(m,
					lambda x: inspect.isclass(x) and
					issubclass(x, BasePlugin) and
					not x == BasePlugin)
			for name, c in classes:
				self.plugins[plugin] = c(
						self.event, self.bot, self)
			self.log.info("Loaded plugin: %s" % plugin)
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
			o = self.plugins[plugin]
			o.unregister()
			if hasattr(o, "cleanup"):
				o.cleanup()
			del o
			del self.plugins[plugin]
			self.log.info("Unloaded plugin: %s" % plugin)
		
	def loadPlugins(self):
		"""E.loadPlugins() -> None

		Load any available plugins loading the global/default
		ones first, then loading the ones found in the
		environment. Plugins found in the environment
		may override existing plugins already loaded.
		"""

		self.plugins = {}
		plugins = default_config.DEFAULT_PLUGINS

		for plugin in plugins:
			self.loadPlugin(plugin)

		plugins = self.config.items("plugins")
		for plugin, enabled in plugins:
			name, attr = plugin.split(".")
			if attr == "enabled" and enabled:
				try:
					self.loadPlugin(name)
				except:
					self.errors += 1
					self.log.error("Coult not load plugin: %s" % name)
					self.log.error(format_exc())
	
	def unloadPlugins(self):
		"""E.unloadPlugins() -> None

		Unload all loaded plugins calling their cleanup
		methods if they exist.
		"""

		for plugin in self.plugins.copy():
			self.unloadPlugin(plugin)

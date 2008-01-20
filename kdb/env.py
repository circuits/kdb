# Filename: env.py
# Module:	env
# Date:		15 June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Environment Container

...
"""

import os
import sys
import weakref
import inspect
from traceback import format_exc

from pymills.timers import Timers
from pymills.event import Manager
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

		self.event = Manager(log=self.log,
				debug=self.config.getboolean("logging", "verbose"))
		self.timers = Timers(self.event)
		self.plugins = weakref.WeakValueDictionary()

		self.bot = Bot(self.event, self)

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

		if plugin in self.plugins:
			self.log.warn("Not loading plugin '%s' - Already loaded!" % plugin)
			return False

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
			del self.plugins[plugin]
			self.log.info("Unloaded plugin: %s" % plugin)

	def loadPlugins(self):
		"""E.loadPlugins() -> None

		Load any available plugins loading the global/default
		ones first, then loading the ones found in the
		environment. Plugins found in the environment
		may override existing plugins already loaded.
		"""

		plugins = list(default_config.DEFAULT_PLUGINS)

		if self.config.has_section("plugins"):
			for name, value in self.config.items("plugins"):
				plugin, attr = name.split(".")
				if attr.lower() == "enabled":
					if plugin not in plugins:
						plugins.append(plugin)

		for plugin in plugins:
			try:
				self.loadPlugin(plugin)
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

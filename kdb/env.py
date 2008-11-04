# Module:	env
# Date:		11th September 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""env - System Environment

System environment that acts as a container of objects in the system for
easier access by other parts of the system including plugins.
Every plugin is passed an instnace of this environment.
"""

import os
import sys
import socket
import inspect
import weakref
from time import time
from traceback import format_exc

from pymills.utils import safe__import__

from circuits.lib import config
from circuits.lib.env import Environment
from circuits import listener, Event, Component, Bridge

from circuits.lib.log import (
		Info as LogInfo,
		Debug as LogDebug,
		Error as LogError,
		Warning as LogWarning,
		Exception as LogException)

import defaults
from bot import Bot
from plugin import BasePlugin

from db import (
		Databases,
		Load as LoadDatabases,
		Create as CreateDatabases)

from __init__ import (
		__name__ as systemName,
		__description__ as systemDesc,
		__version__ as systemVersion)

class SystemEnvironment(Environment):

	version = 1
	name = systemName

	@listener("created")
	def onCREATED(self):
		for section in defaults.CONFIG:
			if not self.config.has_section(section):
				self.config.add_section(section)
			for option, value in defaults.CONFIG[section].iteritems():
				if type(value) == str:
					value = value % {"name": self.name}
				self.config.set(section, option, value)
		self.send(config.Save(), "save", "config")

		self.db = Databases(self)
		self.manager += self.db
		self.send(CreateDatabases(), "create", "db")

	@listener("loaded")
	def onLOADED(self):
		self.db = Databases(self)
		self.manager += self.db
		self.send(LoadDatabases(), "load", "db")

		self.debug = self.config.getboolean("main", "debug", False)
		self.verbose = self.config.getboolean("logging", "verbose", False)

		self.timers = []
		self.plugins = weakref.WeakValueDictionary()

		self.errors = 0
		self.events = 0
		self.sTime = time()

		port = self.config.getint("server", "port", 80)
		address = self.config.get("server", "address", "0.0.0.0")
		ssl = self.config.getboolean("server", "ssl", False)
		bind = self.config.get("server", "bind", None)

		auth = {
				"host": socket.gethostname(),
				"server": address,
				"nick": self.config.get("bot", "nick", systemName),
				"ident": self.config.get("bot", "ident", systemName),
				"name": self.config.get("bot", "name", systemDesc)
		}
		if self.config.has_option("server", "password"):
			auth["password"] = self.config.get("server", "password")

		self.bot = Bot(self,	port, address, ssl, bind, auth)
		self.manager += self.bot

		port = self.config.getint("bridge", "port", 8000)
		address = self.config.get("bridge", "address", "0.0.0.0")
		self.bridge = Bridge(port, address)
		self.manager += self.bridge

	def loadPlugin(self, plugin):
		"""E.loadPlugin(plugin) -> None

		Load a single plugin given by plugin.
		If this plugin is already laoded, it'll be
		replaced.
		"""

		if plugin in self.plugins:
			self.push(
					LogWarning("Not loading plugin '%s' - Already loaded!" % plugin),
					"warning", "log")
			return False

		try:
			fqplugin = "kdb.plugins.%s" % plugin
			if sys.modules.has_key(fqplugin):
				try:
					reload(sys.modules[fqplugin])
				except Exception, err:
					self.push(
							LogError("Problem reloading plugin '%s'" % plugins),
							"error", "log")
					self.push(LogException(err), "exception", "log")
					self.push(LogDebug(format_exc()), "debug", "log")
					return False

			m = safe__import__("plugins.%s" % plugin,
					globals(), locals(), "kdb")

			classes = inspect.getmembers(m,
					lambda x: inspect.isclass(x) and
					issubclass(x, BasePlugin) and
					not x == BasePlugin)
			for name, c in classes:
				o = c(self, self.bot)
				self.manager += o
				self.plugins[plugin] = o
			self.push(LogInfo("Loaded plugin: %s" % plugin), "info", "log")
			return True
		except Exception, err:
			self.push(
					LogError("Problem loading plugin '%s'" % plugin),
					"error", "log")
			self.push(LogException(err), "exception", "log")
			self.push(LogDebug(format_exc()), "debug", "log")
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
			self.push(LogInfo("Unloaded plugin: %s" % plugin), "info", "log")

	def loadPlugins(self):
		"""E.loadPlugins() -> None

		Load any available plugins loading the global/default
		ones first, then loading the ones found in the
		environment. Plugins found in the environment
		may override existing plugins already loaded.
		"""

		plugins = list(defaults.PLUGINS)

		if self.config.has_section("plugins"):
			for name, value in self.config.items("plugins"):
				plugin, comp = name.split(".")
				if value.lower() == "enabled":
					if plugin not in plugins:
						plugins.append(plugin)

		for plugin in plugins:
			try:
				self.loadPlugin(plugin)
			except Exception, err:
				self.errors += 1
				self.push(
						LogError("Failed to load plugin: %s" % plugin),
						"error", "log")
				self.push(LogException(err), "exception", "log")
				self.push(LogDebug(format_exc()), "debug", "log")

	def unloadPlugins(self):
		"""E.unloadPlugins() -> None

		Unload all loaded plugins calling their cleanup
		methods if they exist.
		"""

		for plugin in self.plugins.copy():
			self.unloadPlugin(plugin)

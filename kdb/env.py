# Module:   env
# Date:     11th September 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""env - System Environment

System environment that acts as a container of objects in the system for
easier access by other parts of the system including plugins.
Every plugin is passed an instnace of this environment.
"""

import sys
from time import time
from traceback import format_exc
from collections import defaultdict
from inspect import getmembers, isclass

from pymills.utils import safe__import__

from circuits import Debugger
from circuits.tools import kill
from circuits.app import config
from circuits.app.env import Environment

from circuits.app.log import (
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

from __init__ import __name__ as systemName

class SystemEnvironment(Environment):

    version = 1
    name = systemName

    def created(self):
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

    def loaded(self):
        self.db = Databases(self)
        self.manager += self.db
        self.send(LoadDatabases(), "load", "db")

        self.debug = self.config.getboolean("logging", "debug", False)
        self.verbose = self.config.getboolean("logging", "verbose", False)

        self.plugins = defaultdict(set)

        self.errors = 0
        self.events = 0
        self.sTime = time()

        if self.debug:
            self.manager += Debugger(events=self.verbose, logger=self.log)

        self.bot = Bot(self)
        self.manager += self.bot

    def loadPlugin(self, plugin):
        """E.loadPlugin(plugin) -> None

        Load a single plugin given by plugin.
        If this plugin is already laoded, it'll be
        replaced.
        """

        if plugin in self.plugins:
            msg = "Not loading plugin '%s' - Already loaded!" % plugin
            self.push(LogWarning(msg), "warning", self.log)
            return msg

        try:
            fqplugin = "%s.plugins.%s" % (__package__, plugin)
            if sys.modules.has_key(fqplugin):
                try:
                    reload(sys.modules[fqplugin])
                except Exception, e:
                    msg = "Problem reloading plugin '%s'" % plugin
                    self.push(LogError(msg), "error", self.log)
                    self.push(LogException(e), "exception", self.log)
                    self.push(LogDebug(format_exc()), "debug", self.log)
                    return msg

            moduleName = "plugins.%s" % plugin
            m = safe__import__(moduleName, globals(), locals(), __package__)

            p1 = lambda x: isclass(x) and issubclass(x, BasePlugin)
            p2 = lambda x: x is not BasePlugin
            predicate = lambda x: p1(x) and p2(x)
            plugins = getmembers(m, predicate)

            for name, Plugin in plugins:
                instance = Plugin(self)
                instance.register(self.manager)
                msg = "Registered Component: %s" % instance
                self.push(LogInfo(msg), "info", self.log)
                self.plugins[name].add(instance)

            msg = "Loaded plugin: %s" % plugin
            self.push(LogInfo(msg), "info", self.log)
            return msg
        except Exception, e:
            msg = "Problem loading plugin '%s'" % plugin
            self.push(LogError(msg), "error", self.log)
            self.push(LogException(e), "exception", self.log)
            self.push(LogDebug(format_exc()), "debug", self.log)
            return msg

    def unloadPlugin(self, plugin):
        """E.unloadPlugin(plugin) -> None

        Unload the specified plugin if it has been loaded.
        """

        if plugin in self.plugins:
            instances = self.plugins[plugin]
            for instance in instances:
                kill(instance)
                msg = "Unregistered Component: %s" % instance
                self.push(LogInfo(msg), "info", self.log)
                if hasattr(instance, "cleanup"):
                    instance.cleanup()
                    msg = "Cleaned up Component: %s" % instance
                    self.push(LogDebug(msg), "debug", self.log)
            del self.plugins[plugin]

            msg = "Unloaded plugin: %s" % plugin
        else:
            msg = "Not unloading plugin '%s' - Not loaded!" % plugin

        self.push(LogInfo(msg), "info", self.log)
        return msg

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
                plugin, _ = name.split(".")
                if value.lower() == "enabled":
                    if plugin not in plugins:
                        plugins.append(plugin)

        for plugin in plugins:
            self.loadPlugin(plugin)

    def unloadPlugins(self):
        """E.unloadPlugins() -> None

        Unload all loaded plugins calling their cleanup
        methods if they exist.
        """

        for plugin in self.plugins.copy():
            self.unloadPlugin(plugin)

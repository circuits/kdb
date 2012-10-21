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
from inspect import getmembers, isclass

from pymills.utils import safe__import__
from pymills.datatypes import CaselessDict

from circuits.app import env
from circuits.tools import kill
from circuits.app import config
from circuits import handler, Debugger

from circuits.app.log import Log

from bot import Bot
from plugin import BasePlugin
from default_config import CONFIG


class Environment(env.Environment):

    version = 1
    envname = "kdb"

    def __init__(self, path, envname=envname):
        super(Environment, self).__init__(path, envname)

        self.events = 0
        self.errors = 0

    @handler("create")
    def _on_create(self, *args):
        for section in CONFIG:
            if not self.config.has_section(section):
                self.config.add_section(section)
            for option, value in CONFIG[section].iteritems():
                if type(value) == str:
                    value = value % {"name": self.envname}
                self.config.set(section, option, value)
        self.fire(config.Save(), self.config)

    @handler("ready")
    def _on_ready(self):
        self.verbose = self.config.getboolean("logging", "verbose", False)

        self.plugins = CaselessDict()

        self.sTime = time()

        Debugger(events=self.verbose, logger=self.log).register(self)

        self.bot = Bot(self).register(self)

    def loadPlugin(self, plugin):
        """E.loadPlugin(plugin) -> None

        Load a single plugin given by plugin.
        If this plugin is already laoded, it'll be
        replaced.
        """

        if plugin in self.plugins:
            msg = "Not loading plugin '%s' - Already loaded!" % plugin
            self.fire(Log("warning", msg))
            return msg

        try:
            fqplugin = "%s.plugins.%s" % (__package__, plugin)
            if fqplugin in sys.modules:
                try:
                    reload(sys.modules[fqplugin])
                except Exception, e:
                    msg = "Problem reloading plugin '%s'" % plugin
                    self.fire(Log("error", msg))
                    self.fire(Log("error", e))
                    self.fire(Log("debug", format_exc()))
                    return msg

            moduleName = "plugins.%s" % plugin
            m = safe__import__(moduleName, globals(), locals(), __package__)

            p1 = lambda x: isclass(x) and issubclass(x, BasePlugin)
            p2 = lambda x: x is not BasePlugin
            predicate = lambda x: p1(x) and p2(x)
            plugins = getmembers(m, predicate)

            for name, Plugin in plugins:
                instance = Plugin(self)
                instance.register(self.bot)
                msg = "Registered Component: %s" % instance
                self.fire(Log("info", msg))
                if name not in self.plugins:
                    self.plugins[name] = set()
                self.plugins[name].add(instance)

            msg = "Loaded plugin: %s" % plugin
            self.fire(Log("info", msg))
            return msg
        except Exception, e:
            msg = "Problem loading plugin '%s'" % plugin
            self.fire(Log("error", msg))
            self.fire(Log("error", e))
            self.fire(Log("debug", format_exc()))
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
                self.fire(Log("info", msg))
                if hasattr(instance, "cleanup"):
                    instance.cleanup()
                    msg = "Cleaned up Component: %s" % instance
                    self.fire(Log("debug", msg))
            del self.plugins[plugin]

            msg = "Unloaded plugin: %s" % plugin
        else:
            msg = "Not unloading plugin '%s' - Not loaded!" % plugin

        self.fire(Log("info", msg))
        return msg

    def loadPlugins(self):
        """E.loadPlugins() -> None

        Load any available plugins loading the global/default
        ones first, then loading the ones found in the
        environment. Plugins found in the environment
        may override existing plugins already loaded.
        """

        if self.config.has_section("plugins"):
            for name, value in self.config.items("plugins"):
                plugin, _ = name.split(".")
                if value.lower() == "enabled":
                    self.loadPlugin(plugin)

    def unloadPlugins(self):
        """E.unloadPlugins() -> None

        Unload all loaded plugins calling their cleanup
        methods if they exist.
        """

        for plugin in self.plugins.copy():
            self.unloadPlugin(plugin)

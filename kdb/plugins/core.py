# Module:   core
# Date:     09th May 2005
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Core and Plugin Management

This plugin allows the user to manage other plugins and
kdb's core. You can load/unload plugins on the fly and
rehash kdb forcing it to re-load it's environment.
"""

__version__ = "0.0.3"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from kdb.plugin import BasePlugin


class Core(BasePlugin):
    "Core and Plugin Management"

    def cmdREHASH(self, source, target):
        """Reload environment

        Syntax: RELOAD
        """

        self.env.reload()
        msg = "Environment reloaded"
        return msg

    def cmdPLUGINS(self, source, target):
        """List loaded plugins

        Syntax: PLUGINS
        """

        plugins = self.env.plugins.keys()
        msg = "Plugins loaded: %s" % ", ".join(plugins)
        return msg

    def cmdLOAD(self, source, target, plugin):
        """Load a plugin

        Syntax: LOAD <plugin>
        """

        return self.env.loadPlugin(plugin)

    def cmdRELOAD(self, source, target, plugin):
        """Reload an already loaded plugin

        Syntax: RELOAD <plugin>
        """

        if plugin not in self.env.plugins:
            yield "ERROR: Plugin '%s' is not loaded" % plugin
        else:
            yield self.env.unloadPlugin(plugin)
            yield self.env.loadPlugin(plugin)

    def cmdUNLOAD(self, source, target, plugin):
        """Unload an already loaded plugin

        Note: You cannot unload the "core" plugin.

        Syntax: UNLOAD <plugin>
        """

        if plugin == "core":
            return "ERROR: Unloading the core plugin is disallowed."

        return self.env.unloadPlugin(plugin)

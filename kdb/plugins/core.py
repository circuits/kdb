from circuits import Component

from funcy import first


from ..utils import log
from ..plugin import BasePlugin
from ..plugins import load, unload


class Commands(Component):

    channel = "commands"

    def rehash(self, source, target, args):
        """Reload environment

        Syntax: RELOAD
        """

        self.parent.config.reload_config()
        return log("Configuration reloaded.")

    def plugins(self, source, target, args):
        """List loaded plugins

        Syntax: PLUGINS
        """

        plugins = self.parent.bot.plugins

        return "Plugins: {0:s}".format(" ".join(plugins.keys()))

    def load(self, source, target, args):
        """Load a plugin

        Syntax: LOAD <plugin>
        """

        if not args:
            yield "No plugin specified."

        plugin = first(args.split(" ", 1))

        plugins = self.parent.bot.plugins

        if plugin in plugins:
            yield log("Plugin {0:s} already loaded!", plugin)
        else:
            yield self.fire(load(plugin), "plugins")

    def reload(self, source, target, args):
        """Reload an already loaded plugin

        Syntax: RELOAD <plugin>
        """

        if not args:
            yield "No plugin specified."

        plugin = first(args.split(" ", 1))

        plugins = self.parent.bot.plugins

        if plugin not in plugins:
            yield log("Plugin {0:s} is not loaded!", plugin)
        else:
            yield self.fire(unload(plugin), "plugins")
            yield
            yield self.fire(load(plugin), "plugins")

    def unload(self, source, target, args):
        """Unload an already loaded plugin

        Note: You cannot unload the "core" plugin.

        Syntax: UNLOAD <plugin>
        """

        if not args:
            yield "No plugin specified."

        plugin = first(args.split(" ", 1))

        plugins = self.parent.bot.plugins

        if plugin not in plugins:
            yield log("Plugin {0:s} is not loaded!", plugin)
        elif plugin == "core":
            yield log("Core plugin cannot be unloaded!")
        else:
            yield self.fire(unload(plugin), "plugins")


class Core(BasePlugin):
    """Core and Plugin Management

    This plugin allows the user to manage other plugins and
    kdb's core. You can load/unload plugins on the fly and
    rehash kdb forcing it to re-load it's environment.
    """

    __version__ = "0.0.3"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(Core, self).init(*args, **kwargs)

        Commands().register(self)

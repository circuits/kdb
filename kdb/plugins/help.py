# Module:   help
# Date:     30th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Help Messages

This plugin allows the user to get help for command
of other plugins. It retrieves the __doc__ of the
specified command.
"""

__version__ = "0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from inspect import ismethod, getmembers, getmodule

from kdb.plugin import BasePlugin

class Help(BasePlugin):

    """Help plugin

    Provides commands to display helpful infomration about
    other plugins and their commands.
    See: commands help
    """

    def cmdCOMMANDS(self, source, s=None):
        """Display a list of commands for 'plugin'.
        
        Syntax: COMMANDS <plugin>
        """

        msg = None

        if s is None:
            plugins = ["help"]
        elif s == "*":
            plugins = [x.lower() for x in self.env.plugins.keys()]
        else:
            plugins = [s.lower()]

        commands = []
        for plugin in plugins:
            if plugin in self.env.plugins:
                for o in self.env.plugins[plugin]:
                    commands.extend([x[0][3:].lower() for x in getmembers(
                        o, lambda x: ismethod(x) and
                        callable(x) and x.__name__.startswith("cmd"))])

        if not s == "*":
            msg = "Available commands for %s: %s" % (
                plugin, " ".join(commands))
        else:
            msg = "All available commands: %s" % " ".join(commands)

        if msg is None:
            msg = ["No commands for %s or %s is not loaded" % s]

        return msg

    def cmdHELP(self, source, s=None):
        """Display help for the given command or plugin.
        
        Syntax: HELP <s>
        """

        msg = None

        if s is None:
            s = "help"

        sl = s.lower()
        su = s.upper()

        if sl in self.env.plugins:
            msg = self.env.plugins[sl].__doc__
        else:
            for plugin in self.env.plugins.values():
                if hasattr(plugin, "cmd%s" % su):
                    msg = getattr(
                            getattr(plugin, "cmd%s" % su),
                            "__doc__") or \
                                    "No help available for '%s'. To get a list of commands, type: commands %s" % (s, plugin.__name__.lower())
                    break

        if msg is None:
            msg = "No help available for '%s'. To get a list of plugins, type: plugins" % s

        msg = msg.strip()
        msg = msg.replace("\t\t", "\t")
        msg = msg.replace("\t", "   ")
        msg = msg.split("\n")

        if msg is None:
            msg = ["ERROR: Can't find help for '%s'" % s]

        return msg

    def cmdINFO(self, source, plugin):
        """Display info for the given plugin.
        
        Syntax: INFO plugin
        """

        msg = None

        plugin = plugin.lower()

        if plugin in self.env.plugins:
            m = getmodule(self.env.plugins[plugin])
            name = plugin
            description = m.__dict__.get("__doc__", plugin)
            description = description.split("\n", 1)[0]
            version = m.__dict__.get("__version__", "Unknown")
            author = m.__dict__.get("__author__", "Unknown")
            msg = "%s - %s v%s by %s" % (
                    name, description,
                    version, author)

        if msg is None:
            msg = "No info available for '%s'. To get a list of plugins, type: plugins" % s

        msg = msg.strip()
        msg = msg.replace("\t", "   ")
        msg = msg.split("\n")

        return msg

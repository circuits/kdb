from itertools import chain
from inspect import getmodule


from circuits import Component

from funcy import first


from ..plugin import BasePlugin


def format_msg(msg):
    return (
        msg.strip()
        .replace("\t\t", "\t")
        .replace("\t", "   ")
        .split("\n")
    )


def get_plugin_help(plugin):
    return getattr(plugin, "__doc__", None)


def get_command_help(plugin, command):
    method = getattr(plugin, command, None)
    if method is not None:
        return getattr(method, "__doc__", None)


class Commands(Component):

    channel = "commands"

    def commands(self, source, target, args):
        """Display a list of commands for a given plugin or all plugins.

        Syntax: COMMANDS [<plugin>]
        """

        plugins = self.parent.bot.plugins
        commands = self.parent.bot.commands

        if not args:
            return "All available commands: {0:s}".format(
                " ".join(chain(*commands.values()))
            )

        q = first(args.split(" ", 1))

        if q not in plugins:
            return "No commands for {0:s} or {0:s} is not loaded".format(q)

        return "Available commands for {0:s}: {1:s}".format(
            q, " ".join(commands[q])
        )

    def help(self, source, target, args):
        """Display help for the given command or plugin.

        Syntax: HELP [<command>] | [<plugin>]
        """

        plugins = self.parent.bot.plugins
        command = self.parent.bot.command

        if not args:
            q = "help"
        else:
            q = first(args.split(" ", 1))

        if q in plugins:
            msg = get_plugin_help(plugins[q])
        elif q in command:
            msg = get_command_help(command[q], q)
        else:
            msg = None

        if msg is None:
            msg = (
                "No help available for: {0:s}. "
                "To get a list of plugins, type: plugins"
            ).format(q)

        return format_msg(msg)

    def info(self, source, target, args):
        """Display info for the given plugin.

        Syntax: INFO <plugin>
        """

        plugins = self.parent.bot.plugins

        if not args:
            return "No plugin specified."

        name = first(args.split(" ", 1)).lower()

        if name in plugins:
            m = getmodule(plugins[name])
            description = m.__dict__.get("__doc__", name)
            description = description.split("\n", 1)[0]
            version = m.__dict__.get("__version__", "Unknown")
            author = m.__dict__.get("__author__", "Unknown")
            msg = "{0:s} - {1:s} v{2:s} by {3:s}".format(
                name, description, version, author
            )
        else:
            msg = (
                "No info available for: {0:s}. "
                "To get a list of plugins, type: plugins"
            ).format(name)

        return format_msg(msg)


class Help(BasePlugin):
    """Help plugin

    Provides commands to display helpful infomration about
    other plugins and their commands.
    See: commands help
    """

    __version__ = "0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(Help, self).init(*args, **kwargs)

        Commands().register(self)

# Plugin:   channels
# Date:     3th July 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Channel Management

This plugin manages channels and what channels the bot
joins automatically.
"""


__version__ = "0.0.3"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from circuits import handler, Component
from circuits.protocols.irc import JOIN, PART

from funcy import first, second


from ..utils import log
from ..events import cmd
from ..plugin import BasePlugin


DEFAULTS = ["#circuits"]


class ChannelCommands(Component):

    channel = "commands:channels"

    def add(self, source, target, args):
        """Add a channel to startup join list.

        Syntax: ADD <channel>
        """

        if not args:
            return "No channels specified."

        channel = first(args.split(" ", 1))

        if channel not in self.parent.parent.channels:
            self.parent.parent.channels.append(channel)
            return "Added {0:s} to startup join list".format(channel)
        return "{0:s} already in startup join list".format(channel)

    def remove(self, source, target, args):
        """Remove a channel from startup join list.

        Syntax: REMOVE <channel>
        """

        if not args:
            return "No channels specified."

        channel = first(args.split(" ", 1))

        if channel in self.parent.parent.channels:
            self.parent.parent.channels.remove(channel)
            return "{0:s} removed from startup join list".format(channel)
        return "{0:s} not in join startup list".format(channel)

    def list(self, source, target, args):
        """List channels in startup join list.

        Syntax: LIST
        """

        channels = self.parent.parent.channels

        return "Startup Join List: {0:s}".format(" ".join(channels))


class Commands(Component):

    channel = "commands"

    def __init__(self, *args, **kwargs):
        super(Commands, self).__init__(*args, **kwargs)

        ChannelCommands().register(self)

    def channels(self, source, target, args):
        """Manage channel startup join list

        Syntax: CHANNELS <sub-command>

        See: COMMANDS channels
        """

        if not args:
            yield "No command specified."

        tokens = args.split(" ", 1)
        command, args = first(tokens), (second(tokens) or "")

        event = cmd.create(command, source, target, args)

        try:
            yield (yield self.call(event, "commands:channels"))
        except Exception as error:
            yield "ERROR: {0:s}".format(error)

    def join(self, source, target, args):
        """Join the specified channel.

        Syntax: JOIN <channel>
        """

        if not args:
            return "No channel specified."

        channel = first(args.split(" ", 1))

        if channel:
            msg = log("Joining channel: {0:s}", channel)
            self.fire(JOIN(channel), "bot")
        else:
            msg = log("No channel specified.")

        return msg

    def part(self, source, target, args):
        """Leave the specified channel

        Syntax: PART <channel> [<message>]
        """

        if not args:
            return "No channel specified."

        tokens = args.split(" ", 1)
        channel, message = first(tokens), second(tokens) or "Leaving"

        self.fire(PART(channel, message), "bot")


class Channels(BasePlugin):
    "Channel Management"

    def init(self, *args, **kwargs):
        super(Channels, self).init(*args, **kwargs)

        self.channels = self.config.get("channels", DEFAULTS)

        Commands().register(self)

    @handler("numeric")
    def _on_numeric(self, source, target, numeric, args, message):
        if numeric == 1:
            self.joinchannels()

    def cleanup(self):
        self.config["channels"] = self.channels
        self.config.save_config()

    def joinchannels(self):
        for channel in self.channels:
            self.fire(JOIN(channel))

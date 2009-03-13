# Module:   channels
# Date:     03th July 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Channel Management

This plugin manages channels and what channels the bot
joins automatically.
"""

__version__ = "0.0.3"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from circuits import handler
from circuits.net.protocols.irc import Join, Part

from kdb.plugin import BasePlugin, CommandHandler

class ChannelsCommands(CommandHandler):

    def cmdADD(self, source, channel):
        if channel not in self.parent.channels:
            self.parent.channels.append(channel)
            return "Okay, added %s to startup " \
                    "join list" % channel
        else:
            return "%s is already in my startup " \
                    "join list" % channel

    def cmdDEL(self, source, channel):
        if channel not in self.parent.channels:
            return "%s isn't in my startup join list" % channel
        else:
            self.parent.channels.remove(channel)
            return "Okay, removed %s from my " \
                    "startup join list" % channel

    def cmdLIST(self, source):
        return "I'm configured to join %s " \
                "at startup" % ", ".join(self.parent.channels)

class Channels(BasePlugin):
    "Channel Management"

    def __init__(self, *args, **kwargs):
        super(Channels, self).__init__(*args, **kwargs)

        s = self.env.config.get("bot", "channels", None)
        if s:
            self.mychannels = [x.strip() for x in s.split(",") if x.strip()]
        else:
            self.mychannels = []

    def cleanup(self):
        self.env.config.set("bot", "channels", ",".join(self.mychannels))
        fp = open(self.env.config.filename, "w")
        self.env.config.write(fp)
        fp.close()

    def joinchannels(self):
        for channel in self.mychannels:
            self.push(Join(channel), "JOIN")

    def cmdJOIN(self, source, channel):
        """Join the specified channel
        
        Syntax: JOIN <channel>
        """

        self.push(Join(channel), "JOIN")

        return "Okay"

    def cmdPART(self, source, channel, message="Leaving"):
        """Leave the specified channel
        
        Syntax: PART <channel> [<message>]
        """

        self.push(Part(channel, message), "PART")

        return "Okay"

    def cmdCHANNELS(self, source, command, *args, **kwargs):
        self.env.log.debug(source)
        self.env.log.debug(command)
        return ChannelsCommands(self)(command,
                source, *args, **kwargs)

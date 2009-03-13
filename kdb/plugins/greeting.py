# Module:   greeting
# Date:     14th July 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Greeting

Displays a greeting for users that join the channel.
Users that have been greeted before will not get further
greetings, unless they haven't been seen for over 3 days.
"""

__version__ = "0.0.3"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import os
import marshal
from time import time

from circuits import handler, Event
from circuits.net.protocols.irc import Message

from kdb.plugin import BasePlugin, CommandHandler

class GreetingsCommands(CommandHandler):

    def cmdADD(self, source, greeting):
        if not self.parent.hasGreeting(greeting):
            self.parent.addGreeting(greeting)
            return "Okay, added greeting '%s'" % greeting
        else:
            return "'%s' is already one of my greetings!" % greeting

class Irc(BasePlugin):

    """Greeting plugin

    Displays a greeting for users that join the channel.
    Users that have been greeted before will not get further
    greetings, unless they haven't been seen for over 3 days.

    There are no commands for this plugin.
    """

    def __init__(self, *args, **kwargs):
        super(Irc, self).__init__(*args, **kwargs)

        self._history = {}

        historyFile = os.path.join(
            self.env.path, "ghist.bin")
        if os.path.exists(historyFile):
            fd = file(historyFile, "rb")
            self._history = marshal.load(fd)
            fd.close()

        self._greetings = []

    def cleanup(self):
        historyFile = os.path.join(
            self.env.path, "ghist.bin")
        fd = file(historyFile, "wb")
        marshal.dump(self._history, fd)
        fd.close()

    def hasGreeting(self, greeting):
        return greeting in self._greetings

    def addGreeting(self, greeting):
        self._greetings.append(greeting)
    
    @handler("join")
    def onJOIN(self, nick, channel):
        nick = nick.lower()

        if nick == self("getNick").lower():
            return

        if self._history.has_key(nick):
            if (time() - self._history[nick]) > (60*60*24*3):
                msg = "Welcome back %s :)" % nick
                self.push(Message(channel, msg), "PRIVMSG")
        else:
            msg = "Hello there %s, Welcome to %s" % (nick, channel)
            self.push(Message(channel, msg), "PRIVMSG")

        self._history[nick] = time()

    def cmdGREETINGS(self, source, command, *args, **kwargs):
        return GreetingsCommands(self)(command,
                source, *args, **kwargs)

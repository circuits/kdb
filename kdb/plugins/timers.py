# Module:   timers
# Date:     30th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Timers

This plugin shows how to user the timers module.
Provides a test command to create a message to be
display in x seconds.
"""

__version__ = "0.0.2"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from circuits import handler, Event, Timer
from circuits.net.protocols.irc import Message

from kdb.plugin import BasePlugin

class Message(Event):
    """Message Event

    args: target, message
    """

class Timers(BasePlugin):
    "Timers"

    def timer(self, target, message):
        self.push(Message(target, message), "PRIVMSG")

    def cmdTIMER(self, source, target, length, message="Hello World"):
        """Create a new time with the given length and message
        
        Syntax: TIMER <length> [message]
        """

        try:
            length = int(length)
        except ValueError:
            return  "Invalid length specified"

        self += Timer(length, Message(source, message), "timer", self)

        return "Okay timer set"

# Plugin:   greeting
# Date:     14th July 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Greeting

Displays a greeting for users that join the channel.
Users that have been greeted before will not get further
greetings, unless they haven't been seen for over 3 days.
"""


__version__ = "0.0.3"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from time import time
from random import choice, seed
from traceback import format_exc


from cidict import cidict

from circuits import handler, Component
from circuits.protocols.irc import PRIVMSG

from funcy import first, second


from ..utils import log
from ..events import cmd
from ..plugin import BasePlugin


DEFAULTS = [
    "Hello {0:s}",
    "Heya {0:s}",
    "Hody {0:s}",
    "Hey {0:s}",
    "Hi {0:s}",
    "Yo {0:s}",
]

EXPIRY = 60 * 60  # 1 hour


class GreetingsCommands(Component):

    channel = "commands:greetings"

    def add(self, source, target, args):
        """Add a new greeting.

        Syntax: ADD <greeting>
        """

        if not args:
            return "No greeting specified."

        greeting = args

        data = self.parent.parent.data["greeting"]

        if greeting in data["greetings"]:
            return "Greeting already exists!"

        try:
            greeting.format("foo")
            data["greetings"].append(greeting)
            return "Greeting added."
        except Exception as error:
            msg = log("ERROR: {0:s}", error)
            log(format_exc())
            return msg


class Commands(Component):

    def __init__(self, *args, **kwargs):
        super(Commands, self).__init__(*args, **kwargs)

        GreetingsCommands().register(self)

    def greetings(self, source, target, args):
        """Manage greetings

        Syntax: GREETINGS <sub-command>

        See: COMMANDS greetings
        """

        if not args:
            yield "No command specified."

        tokens = args.split(" ", 1)
        command, args = first(tokens), (second(tokens) or "")

        event = cmd.create(command, source, target, args)

        try:
            yield self.call(event, "commands:greetings")
        except Exception as error:
            yield "ERROR: {0:s}".format(error)


class Greeting(BasePlugin):
    """Greeting plugin

    Displays a greeting for users that join the channel.
    Users that have been greeted before will not get further
    greetings, unless they haven't been seen for over 3 days.

    There are no commands for this plugin.
    """

    def init(self, *args, **kwargs):
        super(Greeting, self).init(*args, **kwargs)

        seed(time())

        self.data.init(
            {
                "greeting": {
                    "history": cidict(),
                    "greetings": DEFAULTS,
                }
            }
        )

        Commands().register(self)

    @handler("join")
    def _on_join(self, source, channel):
        nick = source[0].lower()

        data = self.data["greeting"]

        if nick == self.data.state["nick"].lower():
            return

        if nick in data["history"]:
            if (time() - data["history"].get(nick, time())) > EXPIRY:
                msg = "Welcome back {0:s} :)".format(nick)
                self.fire(PRIVMSG(channel, msg))
            del data["history"][nick]
        else:
            greeting = choice(data["greetings"])
            self.fire(PRIVMSG(channel, greeting.format(nick)))

        data["history"][nick] = time()

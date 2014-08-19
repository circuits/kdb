# Filename: bot.py
# Module:   bot
# Date:     17th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""bot - Bot Module

This module defines the Bot Component which connects to an IRC
Network and reacts to IRC Events. The Bot Component consists
of the TCPClient and IRC Components.
"""


from socket import gethostname
from traceback import format_exc


from circuits.net.events import connect
from circuits.net.sockets import TCPClient
from circuits import handler, BaseComponent
from circuits.protocols.irc import (
    IRC, NICK, NOTICE, PASS, PRIVMSG, USER, ERR_NICKNAMEINUSE
)

from cidict import cidict


import kdb
from .utils import log
from .events import cmd
from .plugin import BasePlugin


def wrapvalue(command, event, value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


class Bot(BaseComponent):

    channel = "bot"

    def init(self, data, config):
        self.data = data
        self.config = config

        self.terminate = False

        self.host = self.config["host"]
        self.port = self.config["port"]

        self.auth = {
            "host": gethostname(),
            "server": self.host,
            "nick": self.config["nick"],
            "ident": kdb.__name__,
            "name": kdb.__description__,
        }

        # command -> plugin
        self.command = cidict()

        # plugin name -> commands
        self.commands = cidict()

        # plugin name -> plugin
        self.plugins = cidict()

        self.data.init(
            {
                "state": {
                    "host": self.auth["host"],
                    "server": self.auth["server"],
                    "nick": self.auth["nick"],
                    "ident": self.auth["ident"],
                    "name": self.auth["name"],
                }
            }
        )

        self.transport = TCPClient(channel=self.channel).register(self)
        self.protocol = IRC(channel=self.channel).register(self)

    def is_addressed(self, source, target, message):
        nick = self.data.state["nick"]
        if nick is None:
            return False, target, message

        if target.lower() == nick.lower() or message.startswith(nick):
            if message.startswith(nick):
                message = message[len(nick):]
            while len(message) > 0 and message[0] in [",", ":", " "]:
                message = message[1:]

            if target.lower() == nick.lower():
                return True, source[0], message
            else:
                return True, target, message
        else:
            return False, target, message

    @handler("registered", channel="*")
    def _on_registered(self, component, manager):
        if component.channel == "commands":
            for event in component.events():
                if event not in self.command:
                    self.command[event] = component

            if component.parent.name in self.commands:
                events = self.commands[component.parent.name]
                events = events.union(component.events())
                self.commands[component.parent.name] = events
            else:
                self.commands[component.parent.name] = set(component.events())

        if isinstance(component, BasePlugin):
            if component.name not in self.plugins:
                self.plugins[component.name] = component

    @handler("unregistered", channel="*")
    def _on_unregistered(self, component, manager):
        if component.channel == "commands":
            for event in component.events():
                if event in self.command:
                    del self.command[event]

        if isinstance(component, BasePlugin):
            if component.name in self.commands:
                del self.commands[component.name]
            if component.name in self.plugins:
                del self.plugins[component.name]

    @handler("ready")
    def _on_ready(self, component):
        self.fire(connect(self.host, self.port))

    @handler("connected")
    def _on_connected(self, host, port=None):
        if "password" in self.auth:
            self.fire(PASS(self.auth["password"]))

        auth = self.auth.get

        ident = auth("ident")
        host = auth("host")
        server = auth("server")
        name = auth("name")
        self.fire(USER(ident, host, server, name))

        nick = auth("nick")
        self.fire(NICK(nick))

    @handler("disconnected")
    def _on_disconnected(self):
        if self.terminate:
            raise SystemExit(0)

        self.fire(connect(self.host, self.port))

    @handler("terminate")
    def _on_terminate(self):
        self.terminate = True

    @handler("nick")
    def _on_nick(self, source, newnick):
        if source[0].lower() == self.data.state["nick"]:
            self.data.state["nick"] = newnick

    @handler("numeric")
    def _on_numeric(self, source, numeric, *args):
        if numeric == ERR_NICKNAMEINUSE:
            newnick = "{0:s}_".format(args[0])
            self.data.state["nick"] = newnick
            self.fire(NICK(newnick))

    @handler("privmsg", "notice")
    def _on_privmsg_or_notice(self, event, source, target, message):
        addressed, target, message = self.is_addressed(
            source, target, message
        )

        Reply = PRIVMSG if event.name == "message" else NOTICE

        if addressed:
            tokens = message.split(" ", 1)
            command = tokens[0].encode("utf-8").lower()
            args = (len(tokens) > 1 and tokens[1]) or ""

            if command not in self.command:
                msg = log("Unknown Command: {0:s}", command)
                self.fire(Reply(target, msg))
            else:
                event = cmd.create(command, source, target, args)

                try:
                    value = yield self.call(event, "commands")
                    if value.errors:
                        etype, evalue, etraceback = value.value
                        msg = log(
                            "ERROR: {0:s}: ({1:s})", evalue, repr(message)
                        )
                        log(format_exc())
                        self.fire(Reply(target, msg))
                    else:
                        for msg in wrapvalue(command, event, value.value):
                            self.fire(Reply(target, msg))
                except Exception as error:
                    msg = log("ERROR: {0:s}: ({1:s})", error, repr(message))
                    log(format_exc())
                    self.fire(Reply(target, msg))

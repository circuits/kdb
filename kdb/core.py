# Module:   core
# Date:     2nd August 2005
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""core - Core Component

Core management component and main loop handler.
All events are processes by this component and
also handles system signals to help reload the
configuration and terminate the system.
"""

import os
import signal
import socket
from time import sleep
from traceback import format_exc

from circuits.tools import graph
from circuits.lib.irc import Quit
from circuits.lib.sockets import Connect
from circuits import listener, Event, Component
from circuits.lib.log import (
        Debug as LogDebug,
        Exception as LogException)

###
### Events
###

class Start(Event):
    """Start(Event) -> Start Event"""

class Run(Event):
    """Run(Event) -> Run Event"""

class Stop(Event):
    """Stop(Event) -> Stop Event"""

class ErrorHandler(Component):

    def __init__(self, env, core, *args, **kwargs):
        super(ErrorHandler, self).__init__(*args, **kwargs)

        self.env = env
        self.core = core

    def error(self, *args, **kwargs):
        if len(args) == 3 and issubclass(args[0], BaseException):
            type, value, traceback = args

            self.env.errors += 1

            log = self.env.log.channel
            self.push(LogException("ERROR: %s" % args[1]), "exception", log)
            self.push(LogDebug(args[2]), "debug", log)

            if self.env.debug and type not in (SystemExit, KeyboardInterrupt):
                if self.core._running:
                    self.push(Stop(), "stop", self.core.channel)

class EventCounter(Component):

    def __init__(self, env, *args, **kwargs):
        super(EventCounter, self).__init__(*args, **kwargs)

        self.env = env

    @listener(type="filter")
    def onEVENT(self, *args, **kwargs):
        self.env.events += 1

class Core(Component):

    channel = "core"

    def __init__(self, env):
        super(Core, self).__init__()

        self._running = True

        signal.signal(signal.SIGHUP, self.rehash)
        signal.signal(signal.SIGTERM, self.stop)

        self.env = env

        self.errorhandler = ErrorHandler(self.env, self)
        self.eventcounter = EventCounter(self.env)
        self.manager += self.errorhandler
        self.manager += self.eventcounter

    def registered(self, manager):
        self.env.loadPlugins()
        self.push(Connect(), "connect", self.env.bot)

    def stop(self, signal=0, stack=0):
        self._running = False
        if self.env.bot.client.isConnected():
            self.push(Quit("Received SIGTERM, terminating..."), self.env.bot)
        self.env.unloadPlugins()
        raise SystemExit, 0

    def rehash(self, signal=0, stack=0):
        self.env.reload()

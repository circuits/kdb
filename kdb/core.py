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
            self.push(LogException("ERROR: %s" % args[1]), "exception", "log")
            self.push(LogDebug(args[2]), "debug", "log")

            if self.env.debug and type not in (SystemExit, KeyboardInterrupt):
                self.push(Stop(), "stop", "core")

class EventCounter(Component):

    def __init__(self, env, *args, **kwargs):
        super(EventCounter, self).__init__(*args, **kwargs)

        self.env = env

    @listener(type="filter")
    def onEVENT(self, *args, **kwargs):
        self.env.events += 1

class Core(Component):

    channel = "core"

    running = False

    def __init__(self, env):
        super(Core, self).__init__()

        signal.signal(signal.SIGHUP, self.rehash)
        signal.signal(signal.SIGTERM, self.stop)

        self.env = env

        self.errorhandler = ErrorHandler(self.env)
        self.eventcounter = EventCounter(self.env)
        self.manager += self.errorhandler
        self.manager += self.eventcounter

    def registered(self):
        self.manager += self.errorhandler
        self.manager += self.eventcounter
        self.env.loadPlugins()
        self.env.bot.connect()

    def stop(self, signal=0, stack=0):
        if self.env.bot.client.isConnected():
            self.env.bot.irc.ircQUIT("Received SIGTERM, terminating...")
        self.env.unloadPlugins()
        raise SystemExit, 0

    def rehash(self, signal=0, stack=0):
        self.env.reload()

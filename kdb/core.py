# Module:   core
# Date:     2nd August 2005
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""core - Core Component

Core management component and main loop handler.
All events are processes by this component and
also handles system signals to help reload the
configuration and terminate the system.
"""

from signal import SIGINT, SIGHUP, SIGTERM

from circuits import handler
from circuits.net.protocols.irc import Quit
from circuits import handler, Event, Component
from circuits.app.log import (
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
                if self.core.running:
                    self.push(Stop(), "stop", self.core.channel)

class EventCounter(Component):

    def __init__(self, env, *args, **kwargs):
        super(EventCounter, self).__init__(*args, **kwargs)

        self.env = env

    @handler(filter=True)
    def onEVENT(self, *args, **kwargs):
        self.env.events += 1

class Core(Component):

    channel = "core"

    def __init__(self, env):
        super(Core, self).__init__()

        self.env = env

        self.errorhandler = ErrorHandler(self.env, self)
        self.eventcounter = EventCounter(self.env)
        self.manager += self.errorhandler
        self.manager += self.eventcounter

    def registered(self, component, manager):
        if component == self:
            self.env.loadPlugins()

    @handler("signal", target="*")
    def signal(self, signal, track):
        if signal == SIGHUP:
            self.rehash()
        elif signal in (SIGINT, SIGTERM):
            self.stop()

    def stop(self):
        self.push(Quit("Received SIGTERM, terminating..."), self.env.bot)
        self.env.unloadPlugins()
        raise SystemExit, 0

    def rehash(self):
        self.env.reload()

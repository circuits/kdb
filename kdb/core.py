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
from traceback import extract_tb, format_list

from circuits import handler
from circuits.app.log import Log
from circuits.net.protocols.irc import Quit
from circuits import handler, Event, Component

class Core(Component):

    channel = "core"

    def __init__(self, env):
        super(Core, self).__init__()

        self.env = env

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

    def rehash(self):
        self.env.reload()

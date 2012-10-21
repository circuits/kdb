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

from circuits.app.log import Log
from circuits.net.protocols.irc import Quit
from circuits import handler, BaseComponent

class Core(BaseComponent):

    channel = "core"

    def __init__(self, env):
        super(Core, self).__init__()

        self.env = env

    @handler("registered")
    def _on_registered(self, component, manager):
        if component == self:
            self.env.loadPlugins()

    @handler("signal", channel="*")
    def signal(self, signal, track):
        if signal == SIGHUP:
            self.fire(LoadConfig(), self.env.config)
        elif signal in (SIGINT, SIGTERM):
            self.fire(Quit("Received SIGTERM, terminating..."), self.env.bot)

    @handler("terminate")
    def _on_terminate(self):
        raise SystemExit(0)

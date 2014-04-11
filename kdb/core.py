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


from circuits.protocols.irc import quit
from circuits import handler, BaseComponent, Timer


from .bot import Bot
from .data import Data
from .utils import log
from .plugins import Plugins
from .events import terminate


class Core(BaseComponent):

    channel = "core"

    def init(self, config):
        self.config = config

        self.data = Data()

        self.bot = Bot(self.config).register(self)

        self.plugins = Plugins(
            init_args=(self.bot, self.data, self.config)
        ).register(self)

        log("Loading plugins...")
        for plugin in self.config["plugins"]:
            self.plugins.load(plugin)

    @handler("signal", channel="*")
    def signal(self, signo, stack):
        if signo == SIGHUP:
            self.config.reload_config()
        elif signo in (SIGINT, SIGTERM):
            self.bot.terminate = True
            Timer(5, terminate()).register(self)
            self.fire(quit("Received SIGTERM, terminating..."), self.bot)
        return True

    @handler("terminate")
    def _on_terminate(self):
        raise SystemExit(0)

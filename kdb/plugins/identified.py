from re import match
from time import time


from circuits import handler, Event


from ..plugin import BasePlugin


class identified(Event):
    """identified Event

    This event is emitted when this plugin has successfully identified to services.
    Useful for other plugins to intercept for coordination based on when the bot
    has or hasn't identified itself to services.

    Args:
      - service (The service the bot identified to)
      - timestamp (The time the bot identified)
    """


class Identified(BasePlugin):
    """Identified Plugin

    This plugin automatically determins when the bot has
    successfully identified itself to services such as
    FreeNode's NickServ based on a configurable pattern
    to look for in NickServ responses from the autoid plugin.

    Configuration::

    [identified]
    nickserv = "NickServ"
    pattern = "^You are now identified.*$"
    """

    __version__ = "0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    @handler("notice")
    def _on_notice(self, event, source, target, message):
        if "identified" not in self.config:
            return

        if "nickserv" not in self.config["identified"]:
            return

        nickserv = self.config["identified"]["nickserv"]

        if not source[0].lower() == nickserv.lower():
            return

        if "pattern" not in self.config["identified"]:
            return

        pattern = self.config["identified"]["pattern"]

        m = match(pattern, message)
        if m is None:
            return

        self.fire(identified(nickserv, time()))
        event.stop()

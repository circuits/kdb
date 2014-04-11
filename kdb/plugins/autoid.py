# Plugin:   autoid
# Date:     3rd July 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Automatic Identification

This plugin automatically identifies the bot to services
if it's nick is registered. The configuration is
provided in the configuration file.
"""


__version__ = "0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from re import match


from circuits import handler
from circuits.protocols.irc import PRIVMSG


from ..plugin import BasePlugin


class AutoID(BasePlugin):
    "Automatic Identification"

    @handler("notice")
    def _on_notice(self, event, source, target, message):
        """Automatically login to pircsrv

        The password is stored in the config file.
        The service nickname is stored in the config file.
        The login pattern is stored in the config file.

        Example::

            [autoid]
            nickserv = pronick
            pattern = .*registered nick.*login
            command = LOGIN {0:s}
            password = password
        """

        if "autoid" not in self.config:
            return

        if "nickserv" not in self.config["autoid"]:
            return

        nickserv = self.config["autoid"]["nickserv"]

        if not source[0].lower() == nickserv.lower():
            return

        if "pattern" not in self.config["autoid"]:
            return

        pattern = self.config["autoid"]["pattern"]

        m = match(pattern, message)
        if m is None:
            return

        if "command" not in self.config["autoid"]:
            return

        if "password" not in self.config["autoid"]:
            return

        command = self.config["autoid"]["command"]
        password = self.config["autoid"]["password"]

        self.fire(PRIVMSG(nickserv, command.format(password)))

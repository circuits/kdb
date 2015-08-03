from re import match


from circuits import handler
from circuits.protocols.irc import PRIVMSG


from ..plugin import BasePlugin


class AutoID(BasePlugin):
    """Automatic Identification

    This plugin automatically identifies the bot to services
    if it's nick is registered. The configuration is
    provided in the configuration file.

    The password is stored in the config file.
    The service nickname is stored in the config file.
    The login pattern is stored in the config file.

    Example::

        [autoid]
        nickserv = "NickServ"
        pattern = "^This nickname is registered.*$"
        command = "IDENTIFY {0:s}"
        password = "password"
    """

    __version__ = "0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    @handler("notice")
    def _on_notice(self, event, source, target, message):
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
        event.stop()

from time import asctime


from circuits import handler
from circuits.protocols.irc import NOTICE, PRIVMSG


import kdb
from ..plugin import BasePlugin


class CTCP(BasePlugin):
    """IRC CTCP Events Plugin

    This plugin provides responses to IRC CTCP Events and
    responds to them appropiately.

    NOTE: There are no commands for this plugin (yet).
    """

    __version__ = "0.3"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    @handler("privmsg", "notice", priority=1.0)
    def _on_privmsg_or_notice(self, event, source, target, message):
        """CTCP Event Handler

        Handle IRC CTCP Events and respond to them
        appropiately.
        """

        addressed, target, message = self.bot.is_addressed(
            source, target, message
        )

        Reply = PRIVMSG if event.name == "privmsg" else NOTICE

        if not addressed:
            return

        if not (message and message[0] == "" and message[-1] == ""):
            return

        tokens = iter(message.strip().lstrip("").rstrip("").split(" "))
        ctcptype = next(tokens, None)

        if ctcptype.lower() == "ping":
            response = ("PING", next(tokens, ""))
        elif ctcptype.lower() == "time":
            response = ("TIME", asctime())
        elif ctcptype.lower() == "version":
            response = (
                "VERSION", "{0:s} - v{1:s} ({2:s})".format(
                    kdb.__name__,
                    kdb.__version__,
                    kdb.__url__
                )
            )
        else:
            response = None

        if response is not None:
            self.fire(Reply(target, "{0:s}".format(" ".join(response))))
            event.stop()

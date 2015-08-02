from circuits import handler


from ..plugin import BasePlugin


class Broadcast(BasePlugin):
    """Broadtcasting Support

    This plugin provides support for listening to broadcast
    messages by listening for a certain pattern of message
    and performing some command or event on that.
    """

    __version__ = "0.1.0"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(Broadcast, self).init(*args, **kwargs)

        self.prefix = self.config.get(
            "broadcast", {}
        ).get("prefix", None) or "@"

    @handler("privmsg", "notice", priority=1.0)
    def _on_privmsg_or_notice(self, event, source, target, message):
        addressed, target, message = self.bot.is_addressed(
            source, target, message
        )

        if not addressed and message and message[0] == self.prefix:
            self.fire(
                type(event)(
                    source,
                    target,
                    "{0:s}, {1:s}".format(
                        self.data.state["nick"],
                        message[1:]
                    )
                )
            )

            event.stop()

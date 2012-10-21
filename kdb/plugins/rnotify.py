# Module:   rnotify
# Date:     30th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Remote Notify

This plugin listens for remote notify and remote scmupdate events
and displays them on the default remote channel.
"""

__version__ = "0.2"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from cPickle import loads

from circuits import handler
from circuits.net.protocols.irc import PRIVMSG

from kdb.plugin import BasePlugin

SCM_UPDATE_TPL = """%(project)s: 8%(committer)s 12%(rev)s \
%(logmsg)s (%(files)s)"""

class Notify(BasePlugin):

    """Notification plugin

    This doesn't have any user commands available.
    This provides notification support via XML-RPC and
    displays messages on the configured channel.

    Depends on: remote
    """

    @handler("scmupdate", channel="remote")
    def remote_scmupdate(self, channel, data):
        channel = channel or self.env.config.get("remote", "channel", None)

        if channel is not None:

            d = loads(data)
            files = d["files"]

            if len(files) > 3:
                d["files"] = "%s ... %d more files" % (
                        " ".join(files[:3]),
                        len(files) - 3)
            else:
                d["files"] = " ".join(files)

            msg = SCM_UPDATE_TPL % d
            self.fire(PRIVMSG(channel, msg))

            return "Message sent to %s" % channel
        else:
            return "Message not received. Remote Channel not configured."

    @handler("notify", channel="remote")
    def remote_notify(self, source="unknown", channel=None, message=""):
        channel = channel or self.env.config.get("remote", "channel", None)

        if channel is not None:

            self.fire(PRIVMSG(channel, "Message from %s:" % source))

            for line in message.split("\n"):
                self.fire(PRIVMSG(channel, line))

            return "Message sent to %s" % channel
        else:
            return "Message not received. Remote Channel not configured."

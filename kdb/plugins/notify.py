# Module:   notify
# Date:     30th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Notify

This plugin listens for xmlrpc.notify and xmlrpc.scmupdate events
and displays them on the default xmlrpc channel.
"""

__version__ = "0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from cPickle import loads

from circuits import handler
from circuits.net.protocols.irc import Message

from kdb.plugin import BasePlugin

SCM_UPDATE_TPL = """%(project)s: 8%(committer)s 12%(rev)s \
%(logmsg)s (%(files)s)"""

class Notify(BasePlugin):

    """Notification plugin

    This doesn't have any user commands available.
    This provides notification support via XML-RPC and
    displays messages on the configured channel.

    Depends on: xmlrpc
    """

    @handler("xmlrpc.scmupdate")
    def xmlrpc_scmupdate(self, data):

        if self.env.config.has_option("xmlrpc", "channel"):
            channel = self.env.config.get("xmlrpc", "channel")
        else:
            channel = None

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
            self.push(Message(channel, msg), "PRIVMSG")

            return "Message sent to %s" % channel
        else:
            return "Message not received. XMLRPC Channel not configured."

    @handler("xmlrpc.notify")
    def xmlrpc_notify(self, source="unknown", message=""):

        if self.env.config.has_option("xmlrpc", "channel"):
            channel = self.env.config.get("xmlrpc", "channel")
        else:
            channel = None

        if channel is not None:

            self.push(Message(channel, "Message from %s:" % source), "PRIVMSG")

            for line in message.split("\n"):
                self.push(Message(channel, line), "PRIVMSG")

            return "Message sent to %s" % channel
        else:
            return "Message not received. XMLRPC Channel not configured."

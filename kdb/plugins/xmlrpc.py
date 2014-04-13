# Plugin:   xmlrpc
# Date:     30th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""XML RPC

This plugin provides an XML-RPC interface to kdb
allowing other plugins to respond to "rpc" events.
"""


__version__ = "0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from traceback import format_exc
from xmlrpclib import ServerProxy


from circuits.web import XMLRPC as XMLRPCDispatcher


from ..plugin import BasePlugin


class XMLRPC(BasePlugin):
    """XMLRPC Plugin

    This plugin provides no user commands. This plugin gives
    XML-RPC support to the system allowing other systems to
    interact with the system and other loaded plugins.

    The "notify" plugin is one such plugin that uses this
    to allow remote machines to send notification messages
    to a configured channel.
    """

    def init(self, *args, **kwargs):
        super(XMLRPC, self).init(*args, **kwargs)

        XMLRPCDispatcher("/rpc", "utf-8", "rpc").register(self)

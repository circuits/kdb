# Plugin:   jsonrpc
# Date:     26th April 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""JSON RPC

This plugin provides an JSON-RPC interface to kdb
allowing other plugins to respond to "rpc" events.
"""


__version__ = "0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from circuits.web import JSONRPC as JSONRPCDispatcher


from ..plugin import BasePlugin


class JSONRPC(BasePlugin):
    """JSONRPC Plugin

    This plugin provides no user commands. This plugin gives
    JSON-RPC support to the system allowing other systems to
    interact with the system and other loaded plugins.

    The "notify" plugin is one such plugin that uses this
    to allow remote machines to send notification messages
    to a configured channel.
    """

    def init(self, *args, **kwargs):
        super(JSONRPC, self).init(*args, **kwargs)

        JSONRPCDispatcher("/json-rpc", "utf-8", "rpc").register(self)

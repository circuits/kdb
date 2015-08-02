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

    __version__ = "0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(XMLRPC, self).init(*args, **kwargs)

        XMLRPCDispatcher("/xml-rpc", "utf-8", "rpc").register(self)

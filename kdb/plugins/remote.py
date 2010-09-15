# Module:   xmlrpc
# Date:     30th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""XML RPC

This plugin provides an XML-RPC interface to kdb
allowing other plugins to respond to "xmlrpc" events.

[xmlrpc]
channel = #lab
"""

__version__ = "0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import xmlrpclib
from traceback import format_exc

from circuits.web import XMLRPC

from kdb.plugin import BasePlugin

def send(url, method, *args):
    try:
        server = xmlrpclib.ServerProxy(url, allow_none=True)
        return getattr(server, method)(*args)
    except Exception, e:
        return "ERROR: %s\n%s" % (e, format_exc())

class Remote(BasePlugin):

    """Remote plugin

    This plugin provides no user commands. This plugin gives
    XML-RPC support to the system allowing other systems to
    interact with the system and other loaded plugins.

    The "notify" plugin is one such plugin that uses this
    to allow remote machines to send XML-RPC notification
    messages to a configured channel.
    """

    def __init__(self, env):
        super(Remote, self).__init__(env)

        self.rpc = XMLRPC("/rpc", self.env.bot)
        self.rpc.register(self)

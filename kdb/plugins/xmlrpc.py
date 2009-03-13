# Module:   xmlrpc
# Date:     30th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""XML RPC

This plugin provides an XML-RPC interface to kdb
allowing other plugins to respond to "xmlrpc" events.

[xmlrpc]
channel = #lab
"""

__version__ = "0.0.8"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import xmlrpclib
from traceback import format_exc

import cherrypy
from cherrypy import expose
from cherrypy.lib import xmlrpc

from circuits import handler, Event
from circuits.app.log import Debug as LogDebug

from kdb.plugin import BasePlugin

def send(url, method, *args):
    try:
        server = xmlrpclib.ServerProxy(url, allow_none=True)
        return getattr(server, method)(*args)
    except Exception, e:
        return "ERROR: %s\n%s" % (e, format_exc())

class RPC(Event):
    "RPC(Event) -> RPC Event"

class Root(BasePlugin):

    @handler(filter=True)
    def event(self, event, *args, **kwargs):
        if isinstance(event, RPC):
            self.push(LogDebug(event), "debug", self.env.log)

    @expose
    def default(self, *vpath, **params):
        args, method = xmlrpc.process_body()

        channel = "xmlrpc.%s" % method
        body = self.send(RPC(*args), channel, self.env.bot)

        conf = cherrypy.request.toolmaps["tools"].get("xmlrpc", {})
        xmlrpc.respond(
                body,
                conf.get("encoding", "utf-8"),
                conf.get("allow_none", True))
        return cherrypy.response.body

class XMLRPC(BasePlugin):

    """XML-RPC plugin

    This plugin provides no user commands. This plugin gives
    XML-RPC support to the system allowing other systems to
    interact with the system and other loaded plugins.

    The "notify" plugin is one such plugin that uses this
    to allow remote machines to send XML-RPC notification
    messages to a configured channel.
    """

    def __init__(self, env):
        super(XMLRPC, self).__init__(env)

        self.root = Root(self.env)
        self.root.register(self)

        cherrypy.config.update({
            "log.screen": False,
            "log.error.file": "",
            "engine.autoreload_on": False,
            "server.socket_host": "0.0.0.0",
            "server.socket_port":  8080,
            "server.thread_pool":  1,
            })

        cherrypy.tree.mount(
                self.root,
                config={
                    "/": {
                        "tools.gzip.on": True,
                        "tools.xmlrpc.on": True,
                        "request.dispatch": cherrypy.dispatch.XMLRPCDispatcher(),
                        "tools.trailing_slash.on": False
                        }
                    })

        try:
            cherrypy.engine.SIGHUP = None
            cherrypy.engine.SIGTERM = None
            cherrypy.engine.start()
        except IOError:
            pass

    def cleanup(self):
        cherrypy.engine.stop()
        cherrypy.engine.exit()

# Filename: xmlrpc.py
# Module:	xmlrpc
# Date:		30th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""XML RPC

This plugin provides an XML-RPC interface to kdb
allowing other plugins to respond to "xmlrpc" events.

[xmlrpc]
channel = #lab
"""

__ver__ = "0.0.8"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import cherrypy
from cherrypy.lib import xmlrpc

from circuits import listener, Event

from kdb.plugin import BasePlugin

class XMLRPCEvent(Event):

	def __init__(self, *args):
		Event.__init__(self, *args)

class Root(BasePlugin):

	@listener(type="filter")
	def onDEBUG(self, event, *args, **kwargs):
		if isinstance(event, XMLRPCEvent):
			self.env.log.debug(event)

	def __call__(self, *vpath, **params):
		args, method = xmlrpc.process_body()

		try:
			r = self.send(XMLRPCEvent(*args), "xmlrpc:%s" % method)
		except UnhandledEvent:
			raise Exception, "No handler found for '%s'" % method

		r = [x for x in r if x is not None]
		body = "\n".join(r)

		conf = cherrypy.request.toolmaps["tools"].get("xmlrpc", {})
		xmlrpc.respond(
				body,
				conf.get("encoding", "utf-8"),
				conf.get("allow_none", True))
		return cherrypy.response.body
	__call__.exposed = True

	index = __call__
	default = __call__

class XMLRPC(BasePlugin):

	"""XML-RPC plugin

	This plugin provides no user commands. This plugin gives
	XML-RPC support to the system allowing other systems to
	interact with the system and other loaded plugins.

	The "notify" plugin is one such plugin that uses this
	to allow remote machines to send XML-RPC notification
	messages to a configured channel.
	"""

	def __init__(self, *args, **kwargs):
		super(XMLRPC, self).__init__(*args, **kwargs)

		self.root = Root(self.bot, self.env)

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
		self.root.unregister()
		cherrypy.engine.stop()
		cherrypy.engine.exit()

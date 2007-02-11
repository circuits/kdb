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

__ver__ = "0.0.3"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import os
import cherrypy
from cherrypy.lib import xmlrpc

from pymills.event import Event, Component, listener

from kdb.plugin import BasePlugin

class XMLRPCEvent(Event):

	def __init__(self, *args):
		Event.__init__(self, *args)

class Root(Component):

	_cp_config = {"tools.xmlrpc.on": True}

	def __init__(self, event, bot, env):
		self.bot = bot
		self.env = env
	
	def __del__(self):
		print "Root.__del__"
		self.unregister()
	
	@listener()
	def onDEBUG(self, event):
		if isinstance(event, XMLRPCEvent):
			self.env.log.debug(event)

	def __call__(self, *vpath, **params):
		args, method = xmlrpc.process_body()

		result = self.event.send(
				XMLRPCEvent(*args),
				self.event.getChannelID("xmlrpc:%s" % method),
				self)

		if result is not None:
			body = result
		else:
			raise Exception, "No handler found for '%s'" % method

		conf = cherrypy.request.toolmaps["tools"].get("xmlrpc", {})
		xmlrpc.respond(
				body,
				conf.get("encoding", "utf-8"),
				conf.get("allow_none", 0))
		return cherrypy.response.body
	__call__.exposed = True

	index = __call__
	default = __call__
	
class XMLRPC(BasePlugin):
	"XML-RPC"

	def __init__(self, event, bot, env):
		BasePlugin.__init__(self, event, bot, env)

		self.root = Root(event, bot, env)

		cherrypy.config.update({
			"log.screen": False,
			"log.error.file": "",
			"environment": "production",
			"engine.autoreload_on": False})

		cherrypy.tree.mount(
				self.root,
				config={
					"/": {
						"tools.xmlrpc.on": True,
						"request.dispatch": cherrypy.dispatch.XMLRPCDispatcher()
						}
					})

		cherrypy.server.quickstart()
		cherrypy.engine.start(blocking=False)
	
	def cleanup(self):
		cherrypy.server.stop()
		cherrypy.engine.stop()
		self.root.unregister()

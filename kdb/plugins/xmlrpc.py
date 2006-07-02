# Filename: xmlrpc.py
# Module:	xmlrpc
# Date:		30th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""XML RPC

This plugin provides an XML-RPC interface to kdb
allowing other plugins to respond to "xmlrpc" events.
"""

__ver__ = "0.0.1"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

import os
import cherrypy

from pymills.event import Event, Component, listener

from kdb.plugin import BasePlugin

class XMLRPCEvent(Event):

	def __init__(self, *args):
		Event.__init__(self, *args)

class Root(Component):

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

	def default(self, method, *args):
		result = self.event.send(
				XMLRPCEvent(*args),
				self.event.getChannelID("xmlrpc:%s" % method),
				self)
		if result is not None:
			return result
		else:
			return "No handler found for '%s'" % method
	default.exposed = True
	
class XMLRPC(BasePlugin):
	"XML-RPC"

	def __init__(self, event, bot, env):
		BasePlugin.__init__(self, event, bot, env)

		cherrypy.root = Root(event, bot, env)
		cherrypy.config.update({
			"xmlrpc_filter.on": True,
			"server.log_to_screen": False,
			"server.log_file": os.path.join(
				env.path, "log", "xmlrpc.log"),
			"server.environment": "production",
			"autoreload.on": False,
			"server.thread_pool": 0})
		cherrypy.server.start(init_only=True)
	
	def cleanup(self):
		cherrypy.server.stop()
		cherrypy.root.unregister()

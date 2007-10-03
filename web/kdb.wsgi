#!/usr/bin/env python

import os
os.environ["PYTHON_EGG_CACHE"] = "/var/cache/eggs"

import sys
sys.stdout = sys.stderr

import atexit
import socket
import cherrypy
import xmlrpclib
import threading
from cherrypy import expose
from StringIO import StringIO
from traceback import format_exc

ROOT = "/usr/share/wsgi/kdb/"

CONFIG = {
		"/": {
			"tools.gzip.on": True,
			"tools.staticdir.root": ROOT
			},

		"/js": {
			"tools.gzip.on": True,
			"tools.staticdir.on": True,
			"tools.staticdir.dir": "js"
			},

		"/css": {
			"tools.staticdir.on": True,
			"tools.staticdir.dir": "css"
			},

		"/img": {
			"tools.staticdir.on": True,
			"tools.staticdir.dir": "img"
			},

		"/tpl": {
			"tools.staticdir.on": True,
			"tools.staticdir.dir": "tpl"
			}
		}

def strip(s, color=False):
	"""strip(s, color=False) -> str

	Strips the : from the start of a string
	and optionally also strips all colors if
	color is True.
	"""

	if len(s) > 0:
		if s[0] == ":":
								s = s[1:]
	if color:
		s = s.replace("\x01", "")
		s = s.replace("\x02", "")
	return s

class Root(object):

	@expose
	def send(self, user="anonymous", message="help"):

		url = "http://daisy:8080/"

		s = StringIO()

		try:
			server = xmlrpclib.ServerProxy(url)
			s.write(server.message(user, message))
		except Exception, e:
			if isinstance(e, socket.error):
				if e[0] == 111:
					s.write("ERROR: %s\n" % e[1])
			else:
				s.write("ERROR: %s\n" % e)
				s.write(format_exc())

		r = s.getvalue()
		if type(r) == str:
			r = r.replace("\n", "<br />")
		s.close()

		return r

	@expose
	def index(self, *args, **kwargs):
		return open("%s/tpl/main.html" % ROOT).read()

cherrypy.config.update(
		{
			"environment": "embedded",
			"request.show_tracebacks": True,
			"request.throw_errors": True
			}
		)

application = cherrypy.Application(Root(), "/")
application.merge(CONFIG)

if cherrypy.engine.state == 0:
	cherrypy.engine.start(blocking=False)
	atexit.register(cherrypy.engine.stop)

def main():
	cherrypy.tree.mount(Root(), "/", CONFIG)

	cherrypy.server.quickstart()
	cherrypy.engine.start()

if __name__ == "__main__":
	main()

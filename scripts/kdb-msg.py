#!/usr/bin/env python

import socket
import xmlrpclib
from traceback import format_exc

def main(url="http://localhost:8080/", message="Test Message"):
	try:
		server = xmlrpclib.ServerProxy(url)
		print server.message(socket.gethostname(), message)
	except Exception, e:
		if isinstance(e, socket.error):
			if e[0] == 111:
				print "ERROR: %s" % e[1]
		else:
			print "ERROR: %s" % e
			print format_exc()

if __name__ == "__main__":
	import sys
	main(*sys.argv[1:])

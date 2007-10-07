#!/usr/bin/env python

"""kdb-hg-update

Script that sends an XML_RPC message to kdb notifying
of updates to a remote hg repository.

To use this, put the following in your .hg/hgrc dir:
[hooks]
changegroup.kdb = kdb-hg-update
"""

__desc__ = "Notify kdb of hg Updates"
__version__ = "0.0.2"
__author__ = "James Mills"
__email__ = "%s, prologic at shortcircuit dot net dot au" % __author__
__url__ = "http://shortcircuit.net.au/~prologic/"
__copyright__ = "CopyRight (C) 2007 by %s" % __author__
__license__ = "GPL"

import os
import socket
import optparse
import xmlrpclib
from traceback import format_exc

from mercurial import hg, ui
from mercurial.node import bin, short

USAGE = "%prog [options]"
VERSION = "%prog v" + __version__

ERRORS = [
		(1, "No XML_RPC URL given. Use -u"),
		]

def parse_options():
	"""parse_options() -> opts, args

	Parse and command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-v", "--verbose",
			action="store_true", default=False, dest="verbose",
			help="Verbose output during operation")
	parser.add_option("-u", "--url",
			action="store", default="http://localhost:8080/",
			dest="url",
			help="Set XML_RPC URL (default: http://localhost:8080/)")

	opts, args = parser.parse_args()

	if opts.url is None:
		parser.exit(ERRORS[0][0], ERRORS[0][1])

	return opts, args

def notify(url="http://localhost:8080/", message="Test Message"):
	try:
		server = xmlrpclib.ServerProxy(url)
		server.notify(socket.gethostname(), message)
	except Exception, e:
		print "ERROR: %s" % e
		print format_exc()

def buildMessage(project, node, src):

	dict = {"project": project}

	rev = bin(node)

	repo = hg.repository(ui.ui(),	os.getcwd())
	ctx = repo.changectx(rev)

	logmsg = ctx.description()

	dict["rev"] = "%d:%s" % (ctx.rev(), short(node))
	dict["committer"] = ctx.user()
	dict["logmsg"] = logmsg
	dict["url"] = src

	files = []
	n = ctx.node()
	f = repo.status(ctx.parents()[0].node(), n)
	for path in f[0]:
		files.append("[M] %s" % path)
	for path in f[1]:
		files.append("[A] %s" % path)
	for path in f[2]:
		files.append("[R] %s" % path)

	s = "\n".join(files)
	dict["files"] = s

	if len(files) > 1:
		format = "%(project)s %(committer)s * %(rev)s %(path)s: %(logmsg)s\nFiles:\n%(files)s"
		dict["path"] = "(%d files)" % len(files)
	else:
		format = "%(project)s %(committer)s * %(rev)s %(path)s: %(logmsg)s"
		dict["path"] = "%s" % files[0]

	return format % dict

def main():
	opts, args = parse_options()

	project = os.path.absename(os.getcwd())
	node = os.getenv("HG_NODE")
	src = os.getenv("HG_URL")

	message = buildMessage(project, node, src)
	notify(opts.url, message)

if __name__ == "__main__":
	main()

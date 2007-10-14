#!/usr/bin/env python

"""kdb-hg-update

Script that sends an XML_RPC message to kdb notifying
of updates to a remote hg repository.

To use this, put the following in your .hg/hgrc dir:
[hooks]
changegroup.kdb = kdb-hg-update
"""

__desc__ = "Notify kdb of hg Updates"
__version__ = "0.0.4"
__author__ = "James Mills"
__email__ = "%s, prologic at shortcircuit dot net dot au" % __author__
__url__ = "http://shortcircuit.net.au/~prologic/"
__copyright__ = "CopyRight (C) 2007 by %s" % __author__
__license__ = "GPL"

import os
import sys
import optparse
import xmlrpclib
from cPickle import dumps
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

def sendUpdate(url, data):
	try:
		server = xmlrpclib.ServerProxy(url)
		print >> sys.stderr, server.scmupdate(dumps(data))
	except Exception, e:
		print >> sys.stderr, "ERROR: %s" % e
		print >> sys.stderr, format_exc()
		raise

def getData(project, node):

	data = {"project": project}

	rev = bin(node)

	repo = hg.repository(ui.ui(),	os.getcwd())
	ctx = repo.changectx(rev)

	logmsg = ctx.description()

	data["rev"] = "%d:%s" % (ctx.rev(), short(node))
	data["committer"] = ctx.user()
	data["logmsg"] = logmsg

	files = []
	n = ctx.node()
	f = repo.status(ctx.parents()[0].node(), n)
	for path in f[0]:
		files.append("[M] %s" % path)
	for path in f[1]:
		files.append("[A] %s" % path)
	for path in f[2]:
		files.append("[R] %s" % path)

	data["files"] = files

	return data

def main():
	opts, args = parse_options()

	project = os.path.basename(os.getcwd())
	node = os.getenv("HG_NODE")

	try:
		sendUpdate(opts.url, getData(project, node))
	except Exception, e:
		print >> sys.stderr, "ERROR: %s" % e
		print >> sys.stderr, format_exc()
		raise SystemExit, 1

if __name__ == "__main__":
	main()

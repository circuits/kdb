#!/usr/bin/env python

"""kdb-git-update

Script that sends an XML_RPC message to kdb notifying
of updates to a remote git repository.

To use this, put the following in $GIT_DIR/hooks/update
branch=${1#refs/heads/}
[ "$branch" = "master" ] && branch=
oldhead=$2
newhead=$3
for commit in $(git-rev-list $newhead ^$oldhead | tac); do
	/path/to/kdb-git-update.py $commit $branch
done
"""

__desc__ = "Notify KDB of GIT Updates"
__version__ = "0.1.0"
__author__ = "James Mills"
__email__ = "%s <prologic@shortcircuit.net.au>" % __author__
__url__ = "http://shortcircuit.net.au/~prologic/"
__copyright__ = "CopyRight (C) 2005 by %s" % __author__
__license__ = "GPL"

import re
import sys
import socket
import optparse
import xmlrpclib
from traceback import format_exc
from popen2 import popen4 as popen

USAGE = "%prog [options] <commit> <branch>"
VERSION = "%prog v" + __version__

ERRORS = [
(1, "Not enough arguments."),
(2, "No project name given. Use -p"),
(3, "No XML_RPC URL given. Use -u")]

def parse_options():
	"""parse_options() -> opts, args

	Parse and command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-v", "--verbose",
			action="store_true", default=False, dest="verbose",
			help="Verbose output during operation")
	parser.add_option("-p", "--project",
			action="store", dest="project",
			help="Set the project name")
	parser.add_option("-u", "--url",
			action="store", default="http://localhost:8080",
			dest="url",
			help="Set XML_RPC URL (default: http://localhost:8080)")

	opts, args = parser.parse_args()

	if len(args) < 2:
		parser.print_help()
		parser.exit(ERRORS[0][0], ERRORS[0][1])
	elif opts.project is None:
		parser.exit(ERRORS[1][0], ERRORS[1][1])
	elif opts.url is None:
		parser.exit(ERRORS[2][0], ERRORS[2][1])

	return opts, args

def notify(url="http://localhost:8080", message="Test Message"):
	try:
		server = xmlrpclib.ServerProxy(url)
		server.notify(socket.gethostname(), message)
	except Exception, e:
		print "ERROR: %s" % e
		print format_exc()

def buildMessage(project, commit, branch):

	dict = {"project": project}

	stdout, stdin  = popen("git-cat-file commit %s" % commit)

	logmsg = ""
	for i, line in enumerate(stdout):
		if i == 0:
			tree = line.split(" ")[1].strip()
		elif i == 1:
			parent = line.split(" ")[1].strip()
		elif i == 2:
			author = filter(
					lambda x: x != "",
					re.split("author (.+)<(.+)> (\d+) \+(\d+)",
						line.strip()))
		elif i == 3:
			committer = filter(
					lambda x: x != "",
					re.split("committer (.+)<(.+)> (\d+) \+(\d+)",
						line.strip()))
		elif i > 4:
			logmsg += "%s\n" % line.strip()

	logmsg = logmsg.strip()
	stdout.close()
	stdin.close()

	dict["rev"] = "r%s" % commit[:12]
	dict["committer"] = committer[1].split("@")[0]
	dict["logmsg"] = logmsg

	stdout, stdin  = popen("git-diff-tree -r %s %s" % (
		parent, tree))

	files = []
	for i, line in enumerate(stdout):
		files.append(
				filter(
					lambda x: x != "",
					re.split("""
(\d+) (\d+) ([a-z\d]+) ([a-z\d]+) \
([A-Z])\t(.*)""", line.lstrip(":").strip())))
	stdout.close()
	stdin.close()

	s = ""
	for i, file in enumerate(files):
		if i < 3:
			s += " %s %s\n" % (file[4], file[5])
		else:
			s += " %d more files... (not displayed)\n" % (len(files) - i)
			break
	s.strip()
	dict["files"] = s


	if len(files) > 1:
		format = "%(project)s %(committer)s * %(rev)s %(path)s: %(logmsg)s\nFiles:\n%(files)s"
		dict["path"] = "(%d files)" % len(files)
	else:
		format = "%(project)s %(committer)s * %(rev)s %(path)s: %(logmsg)s"
		dict["path"] = "/%s" % files[0][5]

	return format % dict

def main():

	opts, args = parse_options()

	commit = args[0]
	branch = args[1]

	message = buildMessage(opts.project, commit, branch)
	notify(opts.url, message)

if __name__ == "__main__":
	main()

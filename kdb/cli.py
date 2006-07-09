# Filename: cli.py
# Module:	cli
# Date:		7th Mar 2005
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Command Line Interface

This module handles the the starting/stopping of the system
and any command-line options.
"""

import optparse

import main
from kdb import __version__ as systemVersion

USAGE = """"%prog [options] <endPath> <command>

commands:
  start    Start %prog
  stop     Stop %prog
  rehash   Rehash (reload environment)
  initenv  Create a new empty environment for %prog.
  upgrade  Upgrade an existing environment."""

VERSION = "%prog v" + systemVersion

def parse_options():
	"""parse_options() -> opts, args

	Parse and command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-n", "--no-fork",
			action="store_true", default=False, dest="nofork",
			help="Don't fork to background")

	(opts, args) = parser.parse_args()
	if len(args) != 2:
		parser.print_help()
		raise SystemExit, 1
	return opts, args

def run():
	"""run() -> None

	Parse command-line options and call main.run()
	Treat opts.nofork as a negative option for daemon
	passed to main..run
	"""

	opts, args = parse_options()
	main.run(args, not opts.nofork)

# Filename: cli.py
# Module:	cli
# Date:		7th Mar 2005
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Command Line Interface

This module handles the the starting/stopping of kdb and
the command-line switches.
"""

import optparse

import main
import kdb

USAGE = """"%prog [options] <endPath> <command>

commands:
  start    Start kdb
  stop     Stop kdb
  rehash   Rehash (re-load config, help, messages)
  initenv  Create a new empty environment for kdb.
  upgrade  Upgrade an existing environment."""

VERSION = "%prog v" + kdb.__version__

def parse_options():
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
	opts, args = parse_options()
	daemon = not opts.nofork
	main.run(daemon, args)

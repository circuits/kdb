# Filename: CLI.py
# Module:   CLI
# Date:     7th Mar 2005
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Command Line Interface

This module handles the the starting/stopping of kdb and
the command-line switches.
"""

import sys
import optparse

from pymills.utils import getProgName

import main
import libkdb

def parse_options():

	parser = optparse.OptionParser(
			usage="%prog [options] [start|stop|restart|rehash]",
			version="%prog " + libkdb.__version__)

	parser.add_option("-n", "--no-fork",
			action="store_true", default=False, dest="nofork",
			help="don't fork to background")

	(opts, args) = parser.parse_args()
	if len(args) != 1:
		parser.print_help()
		raise SystemExit, 1
	return (opts, args)

def run():
	(opts, args) = parse_options()
	daemon = not opts.nofork
	main.run(daemon, args)

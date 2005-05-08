# Filename: CLI.py
# Module:   CLI
# Date:     7th Mar 2005
# Author:   James Mills <prologic@shortcircuit.net.au>

"""CLI

Command Line Interface
"""

import sys

from Utils import getProgName
from CmdOpt import CmdOpt
import libkdb, Main, conf

# Program Usage
usage = "\
%s Ver %s\n\
%s\n\
\n\
Usage: %s [options] command\n\
Options:\n\
        -h, --help         (DIsplay this)\n\
        -n, --nofork       (Don't run as a daemon)\n\
        -V, --version      (Print version and exit)\n\
\n\
Commands:\n\
         start   (Start kdb)\n\
         stop    (Stop kdb)\n\
         restart (Restart kdb)\n\
         rehash  (Reload kdb's Configuration)\n\
" \
% ( \
getProgName(), \
libkdb.__version__, \
libkdb.__copyright__, \
getProgName() \
)

# Get Command Line Options
short = "hnV"
long = ["help", "nofork", "version"]

def main():

	cmdopt = CmdOpt(short, long, usage, False, False)

	opts = cmdopt.options()
	args = cmdopt.args

	if opts.has(("-V", "--version")):
		print libkdb.__version__
		sys.exit(0)
	
	daemon = not opts.has(("-n", "--nofork"))

	if args == []:
		print usage
		sys.exit(0)
	
	Main.run(daemon, args)

main()

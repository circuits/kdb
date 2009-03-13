#!/usr/bin/env python

import sys
import optparse
from socket import gethostname

from kdb.plugins.xmlrpc import send
from kdb import __version__ as systemVersion

USAGE = "%prog [options] message"
VERSION = "%prog v" + systemVersion

###
### Functions
###

def parse_options():
    """parse_options() -> opts, args

    Parse any command-line options given returning both
    the parsed options and arguments.
    """

    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option("-u", "--url",
            action="store", default="http://localhost:8080/", dest="url",
            help="Specify url to send message to (XML-RPC)")

    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        raise SystemExit, 1

    return opts, args

###
### Main
###

def main():
    opts, args = parse_options()

    url = opts.url

    if args[0] == "-":
        message = sys.stdin.read()
    else:
        message = " ".join(args)

    print send(url, "notify", gethostname(), message)

###
### Entry Point
###

if __name__ == "__main__":
    main()

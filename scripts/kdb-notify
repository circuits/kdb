#!/usr/bin/env python

import os
import sys
import optparse
from socket import gethostname

from kdb.plugins.remote import send
from kdb import __version__ as systemVersion

USAGE = "%prog [options] target message"
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
            action="store", default="http://localhost:8000/rpc/", dest="url",
            help="Specify url to send message to (XML-RPC)")

    opts, args = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        raise SystemExit, 1

    return opts, args

###
### Main
###

def main():
    opts, args = parse_options()

    url = opts.url
    target = args[0]

    if args[1] == "-":
        message = sys.stdin.read()
    else:
        message = " ".join(args[1:])

    user = os.environ.get("USER", None)
    hostname = gethostname()
    source = "%s@%s" % (user, hostname)
    print send(url, "remote.message", source, target, message)

###
### Entry Point
###

if __name__ == "__main__":
    main()

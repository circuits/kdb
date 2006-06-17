# Filename: default_config.py
# Module:	default_config
# Date:		15th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Default Configuration

...
"""

import sys

from pymills.config import Configuration

__all__ = ["createConfig", "VERSION"]

VERSION = 1

CONFIG = (
		("kdb", "database", "sqlite://%s/db/kdb.db"),
		("kdb", "pidfile", "%s/log/kdb.pid"),
		("logging", "type", "file"),
		("logging", "file", "kdb.log"),
		("logging", "level", "DEBUG"),
		("connect", "host", "localhost"),
		("connect", "port", "6667"),
		("bot", "ident", "kdb"),
		("bot", "nick", "kdb"),
		("bot", "name", "Knowledge Database Bot"),
		)

def createConfig(filename):
	config = Configuration(filename)
	for section, name, value in CONFIG:
		config.set(section, name, value)
	config.save()

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "Usage: python default_config.py <filename>"
		raise SystemExit, 1
	
	createConfig(sys.argv[1])

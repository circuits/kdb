# Filename: default_config.py
# Module:	default_config
# Date:		15th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id$

"""Default Configuration

...
"""

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
		("bot", "name", "Knowledge Database Bot")
		)

DEFAULT_PLUGINS = (
		"core",
		"help",
		"stats",
		"irc",
		"host",
		"spell",
		"pyint",
		"weather",
		"xmlrpc",
		"notify")

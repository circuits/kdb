# Module:	defaults
# Date:		14th May 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Defaults

System Defaults.
This module contains default configuration and sane defaults for various
parts of the system. These defaults are used by the environment initially
when no environment has been created.
"""

import os

from kdb import __name__ as systemName

CONFIG = (
		("main", "pidfile", os.path.join("log", "%s.pid" % systemName)),
		("main", "debug", False),
		("logging", "type", "file"),
		("logging", "file", os.path.join("log", "%s.log") % systemName),
		("logging", "level", "DEBUG"),
		("connect", "host", "localhost"),
		("connect", "port", "6667"),
		("bot", "ident", "kdb"),
		("bot", "nick", "kdb"),
		("bot", "name", "Knowledge Database Bot")
)

PLUGINS = (
		"core",
		"help",
		"irc",
		"channels",
		"stats",
		)

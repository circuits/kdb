# Filename: conf.py
# Module:   conf
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Config

Config Module
"""

# Prevent execution of this file
if __name__ == "__main__":
	print "This is a config file. Please do not execute it."
	import sys
	sys.exit(0)

#
# Options
#

import os

# Path Settings
paths = {}
paths["base"] = os.getcwd()
paths["plugins"] = "%s/%s" % (paths["base"], "plugins")
paths["data"] = "%s/%s" % (paths["base"], "data")
paths["logs"] = "%s/%s" % (paths["base"], "logs")

# Plugins

plugins = [
	#"hello",
	"factoids",
	"pyint",
	"irccommands",
	"stats",
	"plugins",
	"timer",
	"host",
	"spell",
	#"Trivia",
	"help"]

# Server Settings
servers = []
servers.append(("dede", 6667))

# Channel Settings
channels = [
	"#se",
	"#lab"]

# Bot Settings
me = {}
me["nick"] = "kdb"
me["user"] = "kdb"
me["name"] = "Knowledge (IRC) Bot"

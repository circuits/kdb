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
paths["plugins"] = paths["base"] + "/plugins"
paths["data"] = paths["base"] + "/data"
paths["logs"] = paths["base"] + "/logs"

# Server Settings
servers = []
servers.append(("dede", 6667))

# Channel Settings
channels = ["#ShortCircuit", "#SE"]

# Bot Settings
me = {}
me["nick"] = "kdb"
me["user"] = "kdb"
me["name"] = "ShortCircuit Knowledge Bot"

#" vim: tabstop=3 nocindent autoindent

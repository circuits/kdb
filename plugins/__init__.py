# Filename: __init__.py
# Module:   __init__
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""__init__

This module makes a directory a package
"""

import os
import conf

def load():

def list():
	path = conf.paths["plugins"]
	files = os.listdir(path)
	rm = ["__init__", "Plugin"]
	plugins = []
	for file in files:
		(root, ext) = os.path.splitext(file)
		if ext == (os.path.extsep + "py"):
			if not root in rm:
				plugins.append(root)
	return plugins

#" vim: tabstop=3 nocindent autoindent

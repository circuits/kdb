#!/usr/bin/env python

from distutils.core import setup

import libkdb

setup(name = "kdb",
		version = libkdb.__version__,
		description = libkdb.__desc__,
		author = libkdb.__author__,
		author_email = libkdb.__email__,
		url = libkdb.__url__,
		packages=["libkdb"],
		scripts=["kdb"])

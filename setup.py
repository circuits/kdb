#!/usr/bin/env python

from distutils.core import setup

import kdb

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

__version__ = kdb.__version__

setup(name = "kdb",
		version = kdb.__version__,
		description = kdb.__desc__,
		author = kdb.__author__,
		author_email = kdb.__email__,
		url = kdb.__url__,
		packages=["kdb", "kdb/plugins"],
		scripts=["bin/kdb", "bin/kdb-notify", "bin/kdb-git-update"])

#!/usr/bin/env python

from distutils.core import setup

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

import kdb

pkg = kdb
__version__ = pkg.__version__

setup(
		name=pkg.__name__,
		version=pkg.__version__,
		description=pkg.__description__,
		long_description=pkg.__doc__,
		author=pkg.__author__,
		author_email=pkg.__author_email__,
		maintainer=pkg.__maintainer__,
		maintainer_email=pkg.__maintainer_email__,
		url=pkg.__url__,
		download_url=pkg.__download_url__,
		classifiers=pkg.__classifiers__,
		license=pkg.__license__,
		keywords=pkg.__keywords__,
		platform=pkg.__platform__,

		packages=[
			"kdb",
			"kdb/plugins"
			],

		scripts=[
			"bin/kdb",
			"bin/kdb-notify",
			"bin/kdb-git-update",
			],

		install_requires=[
			"pymills"
			]
		)

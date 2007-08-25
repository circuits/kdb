#!/usr/bin/env python

import os
import re

name = os.path.basename(os.getcwd())
pkg = __import__(name)

try:
	import ez_setup
	ez_setup.use_setuptools()
	print "Using ez_setup"
except ImportError:
	pass

try:
	from setuptools import setup, find_packages
	print "Using setuptools"
except ImportError:
	print "Using distutils"
	from distutils.core import setup

# borrowed from pymills.utils
def getFiles(paths, tests=[os.path.isfile], pattern=".*", \
		include_path=True):
	"""getFiles(path, tests=[os.path.isfile], pattern=".*", \
			include_path=True) -> list of files

	Return a list of files in the specified path
	applying the predicates listed in tests returning
	only the files that match the pattern.
	"""

	def testFile(file):
		for test in tests:
			if not test(file):
				return False
		return True

	list = []
	for path in paths:
		files = os.listdir(path)
		for file in files:
			if testFile(os.path.join(path, file)) and \
					re.match(pattern, file):
				if include_path:
					list.append(os.path.join(path, file))
				else:
					list.append(file)
	return list

def main():
	setup(
		name=name,
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
		platforms=pkg.__platforms__,
		packages=find_packages(),
		scripts=getFiles(["scripts"]),
		install_requires=pkg.__install_requires__,
		setup_requires=pkg.__setup_requires__,
		extras_require=pkg.__extras_require__,
		entry_points=pkg.__entry_points__,
		package_data=pkg.__package_data__,
	)

if __name__ == "__main__":
	main()

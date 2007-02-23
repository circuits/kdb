# Filename: __init__.py
# Module:   __init__
# Date:     04th August 2004
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Knowledge (IRC) Database Bot

kdb is an irc bot that resides on the ShortCircuit IRC
Network and is used as a testbed for testing some aspects
of the PyMills library. kdb offers an extensible
plugin architecture and is completely event-driven.

For more information, come see kdb at
irc://irc.shortcircuit.net.au#lab

/server irc.shortcircuit.net.au
/join #lab
"""

__name__ = "kdb"
__description__ = "Knowledge (IRC) Bot"
__version__ = "0.3.14-2007022400"
__author__ = "James Mills"
__author_email__ = "%s, prologic at shortcircuit dot net dot au" % __author__
__maintainer__ = __author__
__maintainer_email__ = __author_email__
__url__ = "http://shortcircuit.net.au/~prologic/"
__download_url__ = "http://shortcircuit.net.au/~prologic/downloads/software/%s-%s.tar.gz" % (__name__, __version__)
__copyright__ = "CopyRight (C) 2005-2007 by %s" % __author__
__license__ = "GPL"
__platform__ = ""
__keywords__ = "Knowledge Database IRC Bot Framework"
__classifiers__ = [
		"Development Status :: 5 - Production/Stable",
		"Environment :: No Input/Output (Daemon)",
		"Intended Audience :: Developers",
		"Intended Audience :: End Users/Desktop",
		"License :: OSI Approved :: GNU General Public License (GPL)",
		"Natural Language :: English",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Topic :: Communications :: Chat :: Internet Relay Chat",
		"Topic :: Scientific/Engineering :: Artificial Intelligence"
		]
__str__ = "%s-%s" % (__name__, __version__)

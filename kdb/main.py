# Filename: main.py
# Module:	main
# Date:		4th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id: main.py 221 2006-05-28 08:00:12Z prologic $

"""Main

kdb's main module, which runs everything.
"""

import os
import signal
import traceback

from pymills.utils import getProgName, \
		writePID, daemonize

from core import Core
from env import Environment

def run(daemon, args):

	envPath = args[0]
	command = args[1].upper()

	if command == "START":
		start(envPath, daemon)
	elif command == "STOP":
		stop(envPath)
	elif command == "RESTART":
		restart(envPath)
	elif command == "REHASH":
		rehash(envPath)
	elif command == "INITENV":
		initEnv(envPath)
	elif command == "UPGRADE":
		upgrade(envPath)
	else:
		print "ERROR: Invalid Command %s" % args[0]
		raise SystemExit, 1

def start(envPath, daemon=True):

	if not os.path.exists(envPath):
		print "ERROR: Path not found '%s'" % envPath
		raise SystemExit, 1

	env = Environment(envPath)
	if env.needsUpgrade():
		print "ERROR: kdb Environment '%s' needs upgrading" % envPath
		print "Run: %s %s upgrade" % (getProgName, envPath)
		raise SystemExit, 1

	print "-- Starting kdb...\n"

	if daemon:
		daemonize(stderr="/dev/stderr")

	writePID(env.config.get("kdb", "pidfile") % env.path)

	core = Core(env)

	while True:

		try:
			core.run()
		except KeyboardInterrupt:
			core.stop()
			break
		except SystemExit, status:
			break
		except Exception, e:
			print "ERROR: " + str(e)
			print "\nTraceBack follows:\n"
			traceback.print_exc()
			raise SystemExit, 1

	raise SystemExit, 0

def stop(envPath):

	if not os.path.exists(envPath):
		print "ERROR: Path not found '%s'" % envPath
		raise SystemExit, 1

	env = Environment(envPath)

	try:
		os.kill(int(open(env.config.get(
			"kdb", "pidfile") % env.path).read()),
			signal.SIGTERM)
		print "-- kdb Stopped"
	except Exception, e:
		raise
		print "*** ERROR: Could not stop kdb..."
		print str(e)
		raise SystemExit, 1

	raise SystemExit, 0

def restart(envPath):
	stop(envPath)
	start(envPath)

def rehash(envPath):

	if not os.path.exists(envPath):
		print "ERROR: Path not found '%s'" % envPath
		raise SystemExit, 1

	env = Environment(envPath)

	try:
		os.kill(int(open(env.config.get(
			"kdb", "pidfile") % env.path).read()),
			signal.SIGHUP)
		print "-- kdb Rehashed"
	except Exception, e:
		raise
		print "*** ERROR: Could not rehash kdb..."
		print str(e)
		raise SystemExit, 1

	raise SystemExit, 0

def initEnv(envPath):

	if os.path.exists(envPath):
		print "ERROR: Path '%s' already exists" % envPath
		raise SystemExit, 1

	env = Environment(envPath, create=True)

	print "kdb Environment created at %s" % envPath
	print "You can run kdb now:"
	print "   kdb %s start" % envPath

	raise SystemExit, 0

def upgrade(envPath):

	if not os.path.exists(envPath):
		print "ERROR: Path not found '%s'" % envPath
		raise SystemExit, 1

	env = Environment(envPath)
	if not env.needsUpgrade():
		print "ERROR: Upgrade not necessary for kdb Environment %s" % envPath
		raise SystemExit, 1

	env.upgrade()
	print "kdb Environment upgraded."

	raise SystemExit, 0

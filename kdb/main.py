# Filename: main.py
# Module:	main
# Date:		4th August 2004
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Main

This is the main module. Everything starts from here
after the command-line options have been parsed and
passed to here by the cli module.
"""

import os
import signal
import optparse

from pymills.utils import getProgName, \
		writePID, daemonize

from core import Core
from env import Environment
from kdb import __name__ as systemName
from kdb import __version__ as systemVersion

USAGE = """"%prog [options] <endPath> <command>

commands:
  start    Start %prog
  stop     Stop %prog
  rehash   Rehash (reload environment)
  initenv  Create a new empty environment for %prog.
  upgrade  Upgrade an existing environment."""

VERSION = "%prog v" + systemVersion

def parse_options():
	"""parse_options() -> opts, args

	Parse and command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-n", "--no-fork",
			action="store_true", default=False, dest="nofork",
			help="Don't fork to background")

	(opts, args) = parser.parse_args()
	if len(args) != 2:
		parser.print_help()
		raise SystemExit, 1
	return opts, args

def run():
	"""run() -> None

	Parse all command-line arguments and options
	determine what command to run. The environment
	path must be the first argument specified.
	If no valid command is given as the second
	argument, an error is printed and the system
	is terminated with an error code of 1.
	"""

	opts, args = parse_options()

	envPath = args[0]
	command = args[1].upper()

	if command == "START":
		start(envPath, not opts.nofork)
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
	"""start(envPath, daemon=True) -> None

	Start the system. Check if the given envPath is
	valid and doesn't need upgrading. Daemonize if the
	daemon option (default is True) is given. Write the
	pid of this process and run the core.
	"""

	if not os.path.exists(envPath):
		print "ERROR: Path not found '%s'" % envPath
		raise SystemExit, 1

	env = Environment(envPath)
	if env.needsUpgrade():
		print "ERROR: %s Environment '%s' needs upgrading" % (
				systemName, envPath)
		print "Run: %s %s upgrade" % (getProgName, envPath)
		raise SystemExit, 1

	print "-- Starting %s...\n" % systemName

	if daemon:
		daemonize()

	writePID(env.config.get(systemName, "pidfile") % env.path)

	core = Core(env.event, env)
	core.run()

def stop(envPath):
	"""stop(envPath) -> None

	Stop the system by sending the KILL signal to the
	pid found in the environment given by envPath.
	Check if the given environment is valid before
	attempting this. If an error occurs while trying
	to do this, the error is printed and exitcode 1
	is returned.
	"""

	if not os.path.exists(envPath):
		print "ERROR: Path not found '%s'" % envPath
		raise SystemExit, 1

	env = Environment(envPath)

	try:
		os.kill(int(open(env.config.get(
			systemName, "pidfile") % env.path).read()),
			signal.SIGTERM)
		os.remove(env.config.get(
			systemName, "pidfile") % env.path)
		print "-- %s Stopped" % systemName
	except Exception, e:
		print "*** ERROR: Could not stop %s..." % systemName
		print str(e)
		raise SystemExit, 1

def restart(envPath):
	"""restart(envPath) -> None

	Attempt a restart of the system by first stopping the
	system then starting it again.
	"""

	stop(envPath)
	start(envPath)

def rehash(envPath):
	"""rehash(envPath) -> None

	Rehash the system by sending the SIGUP signal to the
	pid found in the environment given by envPath.
	Check if the given environment is valid before
	attempting this. If an error occurs while trying
	to do this, the error is printed and exitcode 1
	is returned.
	"""

	if not os.path.exists(envPath):
		print "ERROR: Path not found '%s'" % envPath
		raise SystemExit, 1

	env = Environment(envPath)

	try:
		os.kill(int(open(env.config.get(
			systemName, "pidfile") % env.path).read()),
			signal.SIGHUP)
		print "-- %s Rehashed" % systemName
	except Exception, e:
		raise
		print "*** ERROR: Could not rehash %s..." % systemName
		print str(e)
		raise SystemExit, 1

	raise SystemExit, 0

def initEnv(envPath):
	"""initEnv(envPath) -> None

	Initialize (create) a new environment using the path
	specified by envPath. Check that the path doesn't
	already exist, printing an error and returning an
	exitcode of 1 if it does.
	"""

	if os.path.exists(envPath):
		print "ERROR: Path '%s' already exists" % envPath
		raise SystemExit, 1

	env = Environment(envPath, create=True)

	print "%s Environment created at %s" % (systemName, envPath)
	print "You can run %s now:" % systemName
	print "   %s %s start" % (systemName, envPath)

	raise SystemExit, 0

def upgrade(envPath):
	"""upgrade(envPath) -> None

	Upgrade the environment at the path specified by
	envPath. Check if the path exists, printing an
	error fna returning an exitcode of 1 if it doesn't.
	Check that the environment actually needs upgrading,
	printing an error if it doesn't and returning an
	exitcode of 1. Otherwise upgrade the environment.
	"""

	if not os.path.exists(envPath):
		print "ERROR: Path not found '%s'" % envPath
		raise SystemExit, 1

	env = Environment(envPath)
	if not env.needsUpgrade():
		print "ERROR: Upgrade not necessary for " \
				"%s Environment %s" % (systemName, envPath)
		raise SystemExit, 1

	env.upgrade()
	print "%s Environment upgraded." % systemName

	raise SystemExit, 0

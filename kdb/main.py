# Module:	main
# Date:		1st October 2007
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""TimeSheet - Main

This is the main module. Everything starts from here
after the command-line options have been parsed and
passed to here by the cli module.
"""

from __future__ import with_statement

import os
import sys
import signal
import optparse
from time import sleep
from traceback import format_exc

from pymills import env
from pymills import event
from pymills.event import *
from pymills.utils import getProgName, writePID, daemonize

from core import Core, Start
from env import SystemEnvironment
from __init__ import __name__ as systemName
from __init__ import __version__ as systemVersion

USAGE = """"%prog [options] <path> <command>

Commands:
  start    Start %prog
  stop     Stop %prog
  rehash   Rehash (reload environment)
  init     Create a new empty environment for %prog.
  upgrade  Upgrade an existing environment."""

VERSION = "%prog v" + systemVersion

###
### Functions
###

def parse_options():
	"""parse_options() -> opts, args

	Parse any command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-d", "--daemon",
			action="store_true", default=False, dest="daemon",
			help="Enable daemon mode")

	opts, args = parser.parse_args()

	if len(args) < 2:
		parser.print_help()
		raise SystemExit, 1

	return opts, args

###
### Errors
###

class Error(Exception): pass

###
### Events
###

class Command(Event):
	"""Command(Event) -> Command Event

	args: command
	"""

###
### Components
###

class Startup(Component):

	channel = "startup"

	def __init__(self, path, opts, command):
		super(Startup, self).__init__()

		self.path = path
		self.opts = opts
		self.command = command

		self.env = SystemEnvironment(path, systemName)

	@listener("registered")
	def onREGISTERED(self):
		self.manager += self.env

		if not self.command == "init":
			if not os.path.exists(self.env.path):
				raise Error("Environment path %s does not exist!" % self.env)
			self.send(env.Load(), "load", self.env.channel)

		self.send(Command(), self.command, self.channel)

	@listener("start")
	def onSTART(self):
		"""onSTART(self) -> None

		Start the system. Daemonize if self.opts.daemon == True
		or if daemon = True is found in the configuration file
		under the [general] section.
		Write the PID of this process to the environment path
		and start the core.
		"""

		print "-- Starting %s...\n" % systemName

		if self.opts.daemon:
			daemonize(path=self.env.path)

		pidfile = self.env.config.get("general", "pidfile")
		if not os.path.isabs(pidfile):
			pidfile = os.path.join(self.env.path, pidfile)
		writePID(pidfile)

		core = Core(self.env)
		self.manager += core
		self.send(Start(), "start", core.channel)

	@listener("stop")
	def onSTOP(self):
		"""onSTOP(self) -> None

		Stop the system by sending the KILL signal to the
		pid found in the environment. If an error occurs
		while trying to do this, the error is printed and
		exitcode 1 is returned.
		"""

		try:
			pidfile = self.env.config.get("general", "pidfile")
			if not os.path.isabs(pidfile):
				pidfile = os.path.join(self.env.path, pidfile)
			with open(pidfile, "r") as f:
				pid = int(f.read().strip())
				os.kill(pid, signal.SIGTERM)
			print "-- %s Stopped" % systemName
		except Exception, err:
			print format_exc()
			raise Error("Cannot stop %s" % systemName)

	@listener("restart")
	def onRESTART(self):
		"""onRESTART(self) -> None

		Attempt a restart of the system by first stopping the
		system then starting it again.
		"""

		self.send(Command(), "stop", self.channel)
		sleep(1)
		self.send(Command(), "start", self.channel)

	@listener("rehash")
	def onREHASH(self):
		"""onREHASH(self) -> None

		Rehash the system by sending the SIGUP signal to the
		pid found in the environment. If an error occurs while
		trying to do this, the error is printed and exitcode 1
		is returned.
		"""

		try:
			pidfile = self.env.config.get("general", "pidfile")
			if not os.path.isabs(pidfile):
				pidfile = os.path.join(self.env.path, pidfile)
			with open(pidfile, "r") as f:
				pid = int(f.read())
				os.kill(pid, signal.SIGHUP)
			print "-- %s Rehashed" % systemName
		except Exception, err:
			raise err
			raise Error("Cannot rehash %s" % systemName)

		raise SystemExit, 0

	@listener("init")
	def onINIT(self):
		"""onINIT(self) -> None

		Initialize (create) a new environment. Check that
		the path doesn't already exist, printing an error
		and returning an exitcode of 1 if it does.
		"""

		if os.path.exists(self.env.path):
			raise Error("Environment path %s already exists!" % self.env.path)

		self.send(env.Create(), "create", self.env.channel)

		print "%s Environment created at %s" % (systemName, self.env.path)
		print "Edit %s/conf/%s.ini" % (self.env.path, systemName)
		print "Start %s:" % systemName
		print " %s %s start" % (getProgName(), self.env.path)

	@listener("upgrade")
	def onUPGRADE(self):
		"""onUPGRADE() -> None

		Upgrade the environment. Check if the path exists,
		printing an error and returning an exitcode of 1 if
		it doesn't exist.
		"""

		if not os.path.exists(self.env.path):
			raise Error("Environment path %s does not exist!" % self.env.path)

		self.send(env.Upgrade(), "upgrade", self.env.channel)
		print "%s Environment upgraded." % systemName

###
### Main
###

def main():
	"""main() -> None

	Parse all command-line arguments and options
	determine what command to run. The environment
	path must be the first argument specified.
	If no valid command is given as the second
	argument, an error is printed and the system
	is terminated with an error code of 1.
	"""

	opts, args = parse_options()

	path = args[0]
	command = args[1].lower()

	event.manager += Startup(path, opts, command)
	event.manager.flush()

###
### Entry Point
###

if __name__ == "__main__":
	main()

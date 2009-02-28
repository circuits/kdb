# Module:   main
# Date:     11th September 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""main - Main Module

This is the main module. Everything starts from here
after the command-line options have been parsed and
passed to here by the cli module.
"""

import os
import signal
import optparse
from time import sleep

from circuits import Event, Component, Manager, Debugger

from circuits.lib.env import (
        Load as LoadEnvironment,
        Create as CreateEnvironment,
        Upgrade as UpgradeEnvironment)

from pymills.utils import writePID, daemonize

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

    def __tick__(self):
        if self.command in ("stop", "restart", "rehash", "init", "upgrade"):
            if len(self.manager) == 0:
                raise SystemExit, 0

    def registered(self):
        self.manager += self.env

        if not self.command == "init":
            if not os.path.exists(self.env.path):
                raise Error("Environment path %s does not exist!" % self.env)
            self.send(LoadEnvironment(), "load", self.env.channel)

        self.send(Command(), self.command, self.channel)

    def start(self):
        """start(self) -> None

        Start the system. Daemonize if self.opts.daemon == True
        or if daemon = True is found in the configuration file
        under the [general] section.
        Write the PID of this process to the environment path
        and start the core.
        """

        if self.opts.daemon:
            daemonize(path=self.env.path)

        pidfile = self.env.config.get("general", "pidfile")
        if not os.path.isabs(pidfile):
            pidfile = os.path.join(self.env.path, pidfile)
        writePID(pidfile)

        self.manager += Core(self.env)

    def stop(self):
        """stop(self) -> None

        Stop the system by sending the KILL signal to the
        pid found in the environment. If an error occurs
        while trying to do this, the error is printed and
        exitcode 1 is returned.
        """

        pidfile = self.env.config.get("general", "pidfile")
        if not os.path.isabs(pidfile):
            pidfile = os.path.join(self.env.path, pidfile)

        with open(pidfile, "r") as f:
            pid = int(f.read().strip())
            os.kill(pid, signal.SIGTERM)

    def restart(self):
        """restart(self) -> None

        Attempt a restart of the system by first stopping the
        system then starting it again.
        """

        self.send(Command(), "stop", self.channel)
        sleep(1)
        self.send(Command(), "start", self.channel)

    def rehash(self):
        """rehash(self) -> None

        Rehash the system by sending the SIGUP signal to the
        pid found in the environment. If an error occurs while
        trying to do this, the error is printed and exitcode 1
        is returned.
        """

        pidfile = self.env.config.get("general", "pidfile")
        if not os.path.isabs(pidfile):
            pidfile = os.path.join(self.env.path, pidfile)

        with open(pidfile, "r") as f:
            pid = int(f.read())
            os.kill(pid, signal.SIGHUP)

    def init(self):
        """init(self) -> None

        Initialize (create) a new environment. Check that
        the path doesn't already exist, printing an error
        and returning an exitcode of 1 if it does.
        """

        if os.path.exists(self.env.path):
            raise Error("Environment path %s already exists!" % self.env.path)

        self.send(CreateEnvironment(), "create", self.env.channel)

    def upgrade(self):
        """upgrade() -> None

        Upgrade the environment. Check if the path exists,
        printing an error and returning an exitcode of 1 if
        it doesn't exist.
        """

        if not os.path.exists(self.env.path):
            raise Error("Environment path %s does not exist!" % self.env.path)

        self.send(UpgradeEnvironment(), "upgrade", self.env.channel)

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

    (Manager() + Debugger(events=False) + Startup(path, opts, command)).run()

###
### Entry Point
###

if __name__ == "__main__":
    main()

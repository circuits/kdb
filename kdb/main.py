# Module:   main
# Date:     11th September 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Main Module"""


import os
import signal
import optparse
from time import sleep

from circuits import handler, Event, BaseComponent, Debugger

from circuits.app import Daemon
from circuits.app import UpgradeEnvironment
from circuits.app import CreateEnvironment, LoadEnvironment

import kdb
from kdb.core import Core
from kdb.env import Environment


USAGE = """"%prog [options] <path> <command>

Commands:
  start    Start %prog
  stop     Stop %prog
  rehash   Rehash (reload environment)
  init     Create a new empty environment for %prog.
  upgrade  Upgrade an existing environment."""

VERSION = "%prog v" + kdb.__version__


def parse_options():
    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option("--daemon",
            action="store_true", default=False, dest="daemon",
            help="Enable daemon mode")

    parser.add_option("-d", "--debug",
            action="store_true",
            default=False, dest="debug",
            help="Enable debug mode")

    opts, args = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        raise SystemExit, 1

    return opts, args


class Error(Exception):
    """Error Exception"""


class Command(Event):
    """Command Event"""


class Startup(BaseComponent):

    channel = "startup"

    def __init__(self, path, opts, command):
        super(Startup, self).__init__()

        self.path = path
        self.opts = opts
        self.command = command

        self.env = Environment(path).register(self)

    def __tick__(self):
        if not self.command == "start" and not self:
            self.stop()

    @handler("environment_loaded", target="env")
    def _on_environment_loaded(self, *args):
        self.push(Command(), self.command, self)

    @handler("exception")
    def _on_exception(self, *args):
        raise SystemExit(-1)

    @handler("started")
    def _on_started(self, component, mode):
        if not self.command == "init":
            if not os.path.exists(self.env.path):
                raise Error("Environment does not exist!")
            else:
                self.push(LoadEnvironment(), target=self.env)
        else:
            if os.path.exists(self.env.path):
                raise Error("Environment already exists!")
            else:
                self.push(Command(), self.command, self)

    @handler("start")
    def _on_start(self):
        if self.opts.daemon:
            pidfile = self.env.config.get("general", "pidfile", "kdb.pid")
            self.manager += Daemon(pidfile=pidfile)

        Core(self.env).register(self)

    @handler("stop")
    def _on_stop(self):
        pidfile = self.env.config.get("general", "pidfile")
        if not os.path.isabs(pidfile):
            pidfile = os.path.join(self.env.path, pidfile)

        f = open(pidfile, "r")
        pid = int(f.read().strip())
        f.close()

        os.kill(pid, signal.SIGTERM)

    @handler("restart")
    def _on_restart(self):
        self.push(Command(), "stop", self.channel)
        sleep(1)
        self.push(Command(), "start", self.channel)

    @handler("rehash")
    def _on_rehash(self):
        pidfile = self.env.config.get("general", "pidfile")
        if not os.path.isabs(pidfile):
            pidfile = os.path.join(self.env.path, pidfile)

        f = open(pidfile, "r")
        pid = int(f.read())
        f.close()

        os.kill(pid, signal.SIGHUP)

    @handler("init")
    def _on_init(self):
        self.push(CreateEnvironment(), target=self.env)

    @handler("upgrade")
    def _on_upgrade(self):
        self.push(UpgradeEnvironment(), target=self.env)


def main():
    opts, args = parse_options()
    (Startup(args[0], opts, args[1]) + Debugger(events=opts.debug)).run()


if __name__ == "__main__":
    main()

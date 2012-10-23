# Module:   main
# Date:     11th September 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Main Module"""


import signal
import optparse
from time import sleep
from os import path, kill

from circuits import handler, Event, BaseComponent, Debugger

from circuits.app import env
from circuits.app import Daemon

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
        raise SystemExit(1)

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

    @handler("ready", channel="env")
    def _on_environment_ready(self):
        self.fire(Command.create(self.command))

    @handler("started")
    def _on_started(self, component):
        if not self.command == "init":
            if not path.exists(self.env.path):
                raise Error("Environment does not exist!")
            else:
                self.fire(env.Load())
        else:
            if path.exists(self.env.path):
                raise Error("Environment already exists!")
            else:
                self.fire(Command(), self.command, self)

    @handler("start")
    def _on_start(self):
        if self.opts.daemon:
            pidfile = self.env.config.get("general", "pidfile", "kdb.pid")
            Daemon(pidfile, path.abspath(self.env.path)).register(self)

        Core(self.env).register(self)

    @handler("stop")
    def _on_stop(self):
        pidfile = self.env.config.get("general", "pidfile")
        if not path.isabs(pidfile):
            pidfile = path.join(self.env.path, pidfile)

        f = open(pidfile, "r")
        pid = int(f.read().strip())
        f.close()

        kill(pid, signal.SIGTERM)

    @handler("restart")
    def _on_restart(self):
        self.fire(Command(), "stop", self.channel)
        sleep(1)
        self.fire(Command(), "start", self.channel)

    @handler("rehash")
    def _on_rehash(self):
        pidfile = self.env.config.get("general", "pidfile")
        if not path.isabs(pidfile):
            pidfile = path.join(self.env.path, pidfile)

        f = open(pidfile, "r")
        pid = int(f.read())
        f.close()

        kill(pid, signal.SIGHUP)

    @handler("init")
    def _on_init(self):
        self.fire(env.Create(), self.env)

    @handler("upgrade")
    def _on_upgrade(self):
        self.fire(env.Create(), self.env)


def main():
    opts, args = parse_options()
    (Startup(args[0], opts, args[1]) + Debugger(events=opts.debug)).run()


if __name__ == "__main__":
    main()

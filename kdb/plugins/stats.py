# Plugin:   stats
# Date:     30th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Statistics

This plugin collects various statistics and allows the
user to access and display them.
"""

__version__ = "0.2.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from os import getpid
from time import clock, time
from collections import Counter
from urllib import urlopen, urlencode


from circuits import handler, Component
from circuits.tools import graph, inspect

from pymills.utils import MemoryStats
from pymills.misc import bytes, duration, buildAverage


import kdb
from ..utils import log
from ..events import cmd
from ..plugin import BasePlugin


class Commands(Component):

    channel = "commands"

    def inspect(self, source, target, args):
        """Display an inspection report of the system

        Syntax; INSPECT
        """

        code = inspect(self.root)
        lang = "Plain Text"
        data = {"code": code, "lang": lang, "submit": "Submit"}
        url = "http://codepad.org/"
        r = urlopen(url, urlencode(data))
        if r.code == 200:
            msg = r.url
        else:
            msg = log("ERROR: {0:d} while posting inspection report", r.code)

        return msg

    def graph(self, source, target, args):
        """Display graph structure of the system

        Syntax; GRAPH
        """

        code = graph(self.root, "kdb")

        lang = "Plain Text"
        data = {"code": code, "lang": lang, "submit": "Submit"}
        url = "http://codepad.org/"
        r = urlopen(url, urlencode(data))

        if r.code == 200:
            msg = r.url
        else:
            msg = log("ERROR: {0:d} while posting graph", r.code)

        return msg

    def errors(self, source, target, args):
        """Display number of errors that have occured

        Syntax: ERRORS
        """

        errors = self.parent.data["errors"]

        if not errors:
            msg = "No errors"
        else:
            msg = "Errors: {0:d}".format(errors)

        return msg

    def uptime(self, source, target, args):
        """Display current uptime and cpu usage

        Syntax: UPTIME
        """

        seconds = time() - self.parent.data["time"]
        uptime = duration(seconds)
        cpu = clock()
        rate = (cpu / seconds) * 100.0

        msg = (
            "Uptime: {0:d}+{1:d}:{2:d}:{3:d} "
            "(CPU: {4:0.2f}s {5:0.2f}%)"
        ).format(*(uptime + (cpu, rate)))

        return msg

    def cstats(self, source, target, args):
        """Display command usage stats

        Syntax: CSTATS
        """

        data = self.parent.data

        time = data["time"]
        commands = data["commands"]

        total_commands = sum(commands.values())

        top5_commands = [
            "{0:s}:{1:d}".format(*x)
            for x in commands.most_common(5)
        ]

        moving_average, _ = buildAverage(time, total_commands)

        msg = (
            "Command Stats: {0:s} "
            "Total: {1:d} "
            "Top 5: {2:s}"
        ).format(
            moving_average,
            total_commands,
            " ".join(top5_commands)
        )

        return msg

    def nstats(self, source, target, args):
        """Display current network stats

        Syntax: NSTATS
        """

        bytesin, bytesout = self.parent.data["bytes"]
        bytestotal = bytesin + bytesout

        msg = "Traffic: {0:s} / {1:s} ({2:s})".format(
            "{0:0.2f}{1:s}".format(*bytes(bytesin)),
            "{0:0.2f}{1:s}".format(*bytes(bytesout)),
            "{0:0.2f}{1:s}".format(*bytes(bytestotal)),
        )

        return msg

    def version(self, source, target, args):
        """Display version information

        Syntax: VERSION
        """

        me = self.parent.bot.auth["nick"]

        msg = "{0:s} [ {1:s} ] v{2:s} by {3:s} - {4:s}".format(
            me,
            kdb.__description__,
            kdb.__version__,
            kdb.__author__,
            kdb.__copyright__,
        )

        return msg

    def mstats(self, source, target, args):
        """Display current memory stats

        Syntax: MSTATS
        """

        m = MemoryStats(getpid())

        msg = "Memory: {0:s} {1:s} {2:s}".format(
            "{0:0.2f}{1:s}".format(*bytes(m.size)),
            "{0:0.2f}{1:s}".format(*bytes(m.rss)),
            "{0:0.2f}{1:s}".format(*bytes(m.stack)),
        )

        return msg

    @handler("events")
    def _on_events(self, source, target, args):
        """Display number of events processed

        Syntax; EVENTS
        """

        return "Events: {0:d}".format(self.parent.data["events"])


class Stats(BasePlugin):

    """Statistics plugin

    Provides various statistical functions and information.
    Namely, network, uptime and error stats.
    See: commands stats
    """

    def init(self, *args, **kwargs):
        super(Stats, self).init(*args, **kwargs)

        self.data.init(
            {
                "commands": Counter(),
                "bytes": (0, 0),
                "time": time(),
                "events": 0,
                "errors": 0,
            }
        )

        Commands().register(self)

    @handler("exception", channel="*")
    def _on_exception(self, *args, **kwargs):
        self.data["errors"] += 1

    @handler(channel="*", priority=101.0)
    def _on_event(self, event, *args, **kwargs):
        self.data["events"] += 1

        if event.name in self.bot.command:
            self.data["commands"][event.name] += 1

    @handler("read")
    def _on_read(self, data):
        bytesin, bytesout = self.data["bytes"]
        bytesin += len(data)
        self.data["bytes"] = (bytesin, bytesout)

    @handler("write")
    def _on_write(self, data):
        bytesin, bytesout = self.data["bytes"]
        bytesout += len(data)
        self.data["bytes"] = (bytesin, bytesout)

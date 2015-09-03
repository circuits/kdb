from os import makedirs, path
from collections import defaultdict
from time import localtime, strftime, time
from datetime import date, datetime, timedelta


from circuits.io import File
from circuits.web import Static
from circuits.io.file import _open
from circuits import handler, Event, Timer
from circuits.io.events import close, write


from ..utils import log
from ..plugin import BasePlugin


def generate_logfile(channel):
    return path.join(channel, "{0:s}.log".format(
        strftime("%Y-%m-%d", localtime()))
    )


class logmsg(Event):
    """logmsg Event"""


class rotatefile(Event):
    """rotatefile Event"""


class Logger(File):

    def init(self, *args, **kwargs):
        super(Logger, self).init(*args, **kwargs)

        interval = datetime.fromordinal((
            date.today() + timedelta(1)
        ).toordinal())

        log("Next log roration set for: {}".format(interval.strftime("%Y-%m-%d %H:%M:%S")))

        Timer(interval, rotatefile(), self.channel).register(self)

    def rotatefile(self):
        channel_dir = path.dirname(self.filename)
        output_dir = path.dirname(channel_dir)
        channel = path.basename(channel_dir)
        logfile = generate_logfile(channel)
        self.fire(close(), self.channel)
        self.fire(_open(path.join(output_dir, logfile), "a"), self.channel)

        interval = datetime.fromordinal((
            date.today() + timedelta(1)
        ).toordinal())

        log("Next log roration set for: {}".format(interval.strftime("%Y-%m-%d %H:%M:%S")))

        Timer(interval, rotatefile(), self.channel).register(self)

    def logmsg(self, message):
        timestamp = strftime("[%H:%M:%S]", localtime(time()))
        self.fire(
            write(
                u"{0:s} {1:s}\n".format(
                    timestamp, message
                ).encode("utf-8")
            ),
            self.channel
        )


class Logging(BasePlugin):
    """Logging Plugin

    A logging plugin that logs any IRC Channels the bot
    happens to be on and writes logs of each channel to
    separate files with log rotation suitable for viewing
    and processing by log analysis tools or web interfaces.

    This will also serve up the RAW IRC Logs at /irclogs/
    via the web plugin. So be sure to enable the web plugin
    too!

    Depends on: web

    Configuration::

    [logging]
    logdir = '/tmp/kdb-logs'

    By default logs are stored in a logs directory in the
    current directory if no configuration is specified.

    There are no commands for this plugin.
    """

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(Logging, self).init(*args, **kwargs)

        # Output log directory
        self.output = self.config.get("logging", {}).get("logdir", "logs")

        # Serve logs at /irclogs
        # Depends on web plugin
        Static("/irclogs/", dirlisting=True, docroot=self.output).register(self)

        # Mapping of IRC Channel -> Logger
        self.loggers = {}

        # Set of channels
        self.ircchannels = set()

        # Mapping of IRC Channel -> Set of Nicks
        self.chanmap = defaultdict(set)

        # Mapping of Nick -> Set of IRC Channels
        self.nickmap = defaultdict(set)

    def create_logger(self, channel):
        if channel in self.loggers:
            return

        if not path.exists(path.join(self.output, channel)):
            makedirs(path.join(self.output, channel))

        self.loggers[channel] = Logger(
            path.join(self.output, generate_logfile(channel)), "a",
            channel="logger.{0:s}".format(channel)
        ).register(self)

    def remove_logger(self, channel):
        if channel not in self.loggers:
            return

        logger = self.loggers[channel]
        logger.unregister()

        del self.loggers[channel]

    @handler("join")
    def join(self, source, channel):
        nick = self.data.state["nick"]
        if source[0].lower() == nick.lower():
            self.create_logger(channel)
            self.ircchannels.add(channel)

        self.chanmap[channel].add(source[0])
        self.nickmap[source[0]].add(channel)

        self.fire(
            logmsg("*** {0:s} has joined {1:s}".format(source[0], channel)),
            "logger.{0:s}".format(channel)
        )

    @handler("part")
    def part(self, source, channel, reason=None):
        nick = self.data.state["nick"]
        if source[0].lower() == nick.lower():
            self.remove_logger(channel)
            self.ircchannels.remove(channel)

        self.chanmap[channel].remove(source[0])
        self.nickmap[source[0]].remove(channel)

        self.fire(
            logmsg(
                "*** {0:s} has left {1:s} ({2:s})".format(
                    source[0], channel, reason or ""
                )
            ),
            "logger.{0:s}".format(channel)
        )

    @handler("quit")
    def quit(self, source, message):
        for ircchannel in self.nickmap[source[0]]:
            self.chanmap[ircchannel].remove(source[0])
            self.fire(
                logmsg("*** {0:s} has quit IRC".format(source[0])),
                "logger.{0:s}".format(ircchannel)
            )

        del self.nickmap[source[0]]

    @handler("privmsg", "notice", priority=100.0)
    def on_privmsg_or_notice(self, source, target, message):
        # Only log messages to the channel we're on
        if target[0] == "#":
            self.fire(
                logmsg(
                    u"<{0:s}> {1:s}".format(
                        source[0], message
                    )
                ),
                "logger.{0:s}".format(target)
            )

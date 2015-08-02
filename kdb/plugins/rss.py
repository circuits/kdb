from itertools import chain
from time import mktime, time
from pickle import dumps, loads
from traceback import format_exc


from circuits.protocols.irc import PRIVMSG
from circuits import handler, task, Event, Timer, Component

from feedparser import parse as parse_feed

from funcy import first, second

from html2text import html2text


from ..utils import log
from ..plugin import BasePlugin


def check_feed(feed):
    return feed()


class check_feeds(Event):
    """check_feeds Event"""


class Feed(object):

    def __init__(self, url, target, interval=60):
        self.url = url
        self.target = target
        self.interval = interval

        self.entries = []
        self.title = ""
        self.link = ""

        self.next = 0
        self.reset()

    def reset(self):
        self.next = time() + (self.interval * 60)

    def __call__(self):
        d = parse_feed(self.url)

        if self.title == "" and self.link == "":
            self.title = getattr(d.feed, "title", "")
            self.link = getattr(d.feed, "link", "")

        new = []
        for v in d.entries:
            e = {
                "time": mktime(v.updated_parsed),
                "title": v.title,
                "summary": html2text(v.summary).strip().split("\n")[0],
                "link": v.links[0].href
            }

            if e not in self.entries:
                self.entries.append(e)
                new.append(e)

        if not new == []:
            s = []
            s.append("RSS: {0:s} ({1:s})".format(self.title, self.link))

            for e in new[:3]:
                x = sum([len(e["title"]), len(e["summary"]), len(e["link"])])
                if x > 450:
                    y = sum([len(e["title"]), len(e["link"])])
                    s.append(
                        " * {0:s}: {1:s} ... <{2:s}>".format(
                            e["title"],
                            e["summary"][:(450 - y)],
                            e["link"]
                        )
                    )
                else:
                    s.append(
                        " * {0:s}: {1:s} <{2:s}>".format(
                            e["title"],
                            e["summary"],
                            e["link"]
                        )
                    )
            return s
        else:
            return []


class Commands(Component):

    channel = "commands"

    def radd(self, source, target, args):
        """Add a new RSS feed to be checked at the given interval.

        Intervan is in minutes.

        Syntax: RADD <url> [<interval>]
        """

        if not args:
            yield "No URL specified."

        tokens = args.split(" ", 2)
        url = first(tokens)
        interval = second(tokens) or "60"

        try:
            interval = int(interval)
        except Exception, error:
            log("ERROR: {0:s}\n{1:s}", error, format_exc())
            yield "Invalid interval specified."

        if interval > 60:
            yield "Interval must be less than 60 minutres."

        feeds = self.parent.data["feeds"]

        feed = Feed(url, target, interval)

        if target in feeds:
            feeds[target].append(feed)
        else:
            feeds[target] = [feed]

        value = yield self.call(
            task(
                check_feed,
                feed,
            ),
            "workerprocesses"
        )

        yield value.value

    def rdel(self, source, target, args):
        """Delete an RSS feed.

        Syntax: RDEL <n>
        """

        if not args:
            return "No feed number. specified."

        n = args

        feeds = self.parent.data["feeds"]

        if target in feeds:
            try:
                n = int(n)
            except Exception, error:
                log("ERROR: {0:s}\n{1:s}", error, format_exc())
                return "Invalid feed number specified."

            if n > 0 and n <= len(feeds[target]):
                del feeds[target][(n - 1)]
                msg = "Feed {0:d} deleted.".format(n)
            else:
                msg = "Invalid feed number specified."
        else:
            msg = "No feeds to delete."

        return msg

    def read(self, source, target, args):
        """Read an RSS feed.

        Syntax: READ <n>
        """

        if not args:
            return "No feed number. specified."

        n = args

        feeds = self.parent.data["feeds"]

        if target in feeds:
            try:
                n = int(n)
            except Exception, error:
                log("ERROR: {0:s}\n{1:s}", error, format_exc())
                return "Invalid feed number specified."

            if n > 0 and n <= len(feeds[target]):
                feed = feeds[target][n]
                msg = feed()
                feed.reset()
            else:
                msg = "Invalid feed number specified."
        else:
            msg = "No feeds to read."

        return msg

    def rlist(self, source, target, args):
        """List all active RSS feeds.

        Syntax: RLIST
        """

        feeds = self.parent.data["feeds"]

        if target in feeds:
            msg = ["RSS Feeds ({0:s}):".format(target)]
            for i, feed in enumerate(feeds[target]):
                msg.append((
                    " {0:d}. {1:s} ({2:s}) / {3:d}mins "
                    "(Next Update in {4:d}mins)").format(
                        (i + 1), feed.title, feed.url,
                        feed.interval, int((feed.next - time()) / 60)
                    )
                )
        else:
            msg = "No feeds available."

        return msg


class RSS(BasePlugin):
    """RSS Aggregator plugin

    Provides RSS aggregation functions allowing you to
    create public or private RSS feeds that are downlaoded
    at regular intervals and checked and display.

    See: COMMANDS rss
    """

    __version__ = "0.0.8"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(RSS, self).init(*args, **kwargs)

        filename = self.config.get("rss", {}).get("filename", None)

        if filename is not None:
            self.data.init(
                {
                    "feeds": self.load(filename)
                }
            )
        else:
            self.data.init(
                {
                    "feeds": {}
                }
            )

        Commands().register(self)

        Timer(60, check_feeds(), persist=True).register(self)

    def cleanup(self):
        filename = self.config.get("rss", {}).get("filename", None)
        if filename is not None:
            self.save(filename)

    def load(self, filename):
        with open(filename, "rb") as f:
            try:
                return loads(f.read())
            except Exception, error:
                log("ERROR: {0:s}\n{1:s}", error, format_exc())
                return {}

    def save(self, filename):
        with open(filename, "wb") as f:
            f.write(dumps(self.data["feeds"]))

    @handler("check_feeds")
    def _on_check_feeds(self):
        feeds = self.data["feeds"]
        for feed in chain(*feeds.values()):
            if feed.next < time():
                for line in feed():
                    self.fire(PRIVMSG(feed.target, line))
                feed.reset()

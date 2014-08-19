# Plugin:   web
# Date:     18th March 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Web Interface

This plugin provides a Web Interface to the system allowing the system
to be interacted with via a Web Browser.
"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from os import path
from cgi import escape
from traceback import format_exc
from os.path import dirname, abspath


from circuits.protocols.irc import strip
from circuits import handler, task, Component
from circuits.web import Server, Controller, JSONRPC, Static


import mako
from mako.lookup import TemplateLookup

from requests import head


import kdb
from kdb.utils import log
from kdb.events import cmd
from kdb.bot import wrapvalue
from kdb.plugin import BasePlugin


BASE = abspath(dirname(__file__))
DOCROOT = path.join(BASE, "static")

print "BASE:", BASE
print "DOCROOT:", DOCROOT

templates = TemplateLookup(
    directories=[path.join(BASE, "templates")],
    module_directory="/tmp",
    output_encoding="utf-8"
)

DEFAULTS = {
    "title": "{0:s} v{1:s} - {2:s}".format(
        kdb.__name__,
        kdb.__version__,
        kdb.__description__
    ),
    "software": "{0:s} v{1:s}".format(
        kdb.__name__,
        kdb.__version__,
    ),
}


def check_url(url):
    return head(url)


def render(name, **d):
    try:
        d.update(DEFAULTS)
        tpl = templates.get_template(name)
        return tpl.render(**d)
    except:
        return mako.exceptions.html_error_template().render()


class Commands(Component):

    channel = "commands"

    def status(self, source, target, args):
        """Report Web Status

        Syntax: STATUS
        """

        try:
            url = self.parent.server.http.base
            value = yield self.call(task(check_url, url), "workerthreads")
            response = value.value
            response.raise_for_status()
            yield "Web: Online"
        except Exception as error:
            yield "Web: Offline ({0:s})".format(error)


class API(Component):

    channel = "api"

    @handler()
    def _on_api_event(self, event, *args, **kwargs):
        if event.channels != (self.channel,):
            return

        command = event.name

        if command not in self.parent.bot.command:
            yield log("Unknown Command: {0:s}", command)
        else:
            args = " ".join(args)
            event = cmd.create(command, None, None, args)

            try:
                value = yield self.call(event, "commands")
                yield "\n".join(
                    escape(strip(msg))
                    for msg in wrapvalue(command, event, value.value)
                )
            except Exception as error:
                message = "{0:s} {1:s}".format(command, " ".join(args))
                yield log("ERROR: {0:s}: ({1:s})", error, repr(message))
                log(format_exc())


class Root(Controller):

    def index(self):
        return render("index.html")


class Web(BasePlugin):
    """Web Plugin

    This plugin provides no user commands. This plugin provides
    a Web Interface to the system allowing the system to be
    interacted with via a Web Browser.
    """

    def init(self, *args, **kwargs):
        super(Web, self).init(*args, **kwargs)

        self.bind = self.config.get(
            "web", {}
        ).get(
            "bind", "0.0.0.0:8000"
        )

        self.docroot = self.config.get(
            "web", {}
        ).get(
            "docroot", DOCROOT
        )

        self.server = Server(self.bind).register(self)

        Static(docroot=self.docroot).register(self)
        JSONRPC("/api", "utf-8", "api").register(self)
        API().register(self)
        Root().register(self)

        Commands().register(self)

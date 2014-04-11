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
from circuits.web import Server, Controller, Static

import mako
from mako.lookup import TemplateLookup


import kdb
from ..utils import log
from ..events import cmd
from ..bot import wrapvalue
from ..plugin import BasePlugin


DOCROOT = abspath(path.join(dirname(__file__), "../../web"))

templates = TemplateLookup(
    directories=[path.join(DOCROOT, "tpl")],
    module_directory="/tmp",
    output_encoding="utf-8"
)

DEFAULTS = {
    "software": "kdb/%s" % kdb.__version__
}


def render(name, **d):
    try:
        d.update(DEFAULTS)
        tpl = templates.get_template(name)
        return tpl.render(**d)
    except:
        return mako.exceptions.html_error_template().render()


class Root(Controller):

    tpl = "index.html"

    def __init__(self, bot, config):
        super(Root, self).__init__()

        self.bot = bot
        self.config = config

    def index(self):
        return render(self.tpl)

    def message(self, message):
        tokens = message.split(" ", 1)
        command = tokens[0].encode("utf-8").lower()
        args = (len(tokens) > 1 and tokens[1]) or ""

        if command not in self.bot.command:
            yield log("Unknown Command: {0:s}", command)
        else:
            event = cmd.create(command, None, None, args)

            try:
                value = yield self.call(event, "commands")
                for msg in wrapvalue(command, event, value.value):
                    yield escape(strip(msg))
            except Exception as error:
                yield log("ERROR: {0:s}: ({1:s})", error, repr(message))
                log(format_exc())


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

        Server(self.bind).register(self)
        Static(docroot=self.docroot).register(self)
        Root(self.bot, self.config).register(self)

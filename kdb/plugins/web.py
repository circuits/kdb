# Module:   web
# Date:     18th March 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Web

This plugin provides a Web Interface to the system allowing the system
to be interacted with via a Web Browser.
"""

__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from os import path
from cgi import escape
from os.path import dirname, abspath

import mako
from mako.lookup import TemplateLookup

from circuits import handler, Event
from circuits.net.protocols import irc
from circuits.tools import graph, inspect
from circuits.web import Server, Controller, Static, Logger

import kdb
from kdb.plugin import BasePlugin

DOCROOT = abspath(path.join(dirname(__file__), "../../web"))

templates = TemplateLookup(
    directories=[path.join(DOCROOT, "tpl")],
    module_directory="/tmp",
    output_encoding="utf-8")

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

    def __init__(self, env):
        super(Root, self).__init__()

        self.env = env

    def index(self):
        return render(self.tpl)

    def message(self, message):
        ourself = self.env.bot.auth["nick"]

        e = irc.Message("anonymous", ourself, message)
        r = self.send(e, target=self.env.bot)

        if not r:
            r = "No response"
        elif type(r) is list:
            r = "\n".join(r)

        r = irc.strip(r, True)
        r = r.replace("\n", "<br>")
        r = escape(r)

        return r

class Web(BasePlugin):

    """Web Plugin

    This plugin provides no user commands. This plugin provides
    a Web Interface to the system allowing the system to be
    interacted with via a Web Browser.
    """

    def __init__(self, env):
        super(Web, self).__init__(env)

        self.bind = self.env.config.get("web", "bind", "0.0.0.0:8000")
        self.docroot = self.env.config.get("web", "docroot", DOCROOT)

        self += (
                Server(self.bind)
                + Static(docroot=self.docroot)
                + Logger(logger=self.env.log)
                + Root(self.env)
                )

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
from circuits.app.log import Debug as LogDebug
from circuits.tools import graph, dotgraph, inspect
from circuits.web import Server, Controller, dispatchers, loggers

import kdb
from kdb.plugin import BasePlugin

docroot = abspath(path.join(dirname(__file__), "../../web"))

templates = TemplateLookup(
    directories=[path.join(docroot, "tpl")],
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

    def graph(self):
        return escape(graph(self.env.root))

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

        self += (
                Server(8000, docroot=docroot)
                + loggers.Logger(logger=self.env.log)
                + Root(self.env)
                )

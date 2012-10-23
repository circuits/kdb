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

from circuits.net.protocols import irc
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
        import pdb; pdb.set_trace()

        ourself = self.env.bot.auth["nick"]

        event = irc.Message("@anonymous", ourself, message)
        value = self.fire(event, self.env.bot.channel)
        for _ in self.wait(event.name):
            yield _

        import pdb; pdb.set_trace()

        if not value:
            response = "No response"
        elif type(value) is list:
            response = "\n".join(value)

        response = irc.strip(response, True)
        response = response.replace("\n", "<br>")
        response = escape(response)

        yield response


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


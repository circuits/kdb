#!/usr/bin/env python

import os
import socket
import xmlrpclib
from StringIO import StringIO
from traceback import format_exc

import mako
from mako.lookup import TemplateLookup

from circuits import Debugger
from circuits.web import Server, Controller

import kdb

templates = TemplateLookup(
    directories=[os.path.join(os.path.dirname(__file__), "tpl")],
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
    url = "http://localhost:8080/"

    def send(self, source="anonymous", target="kdb", message="help"):
        s = StringIO()

        try:
            server = xmlrpclib.ServerProxy(self.url)
            s.write(server.message(source, target, message))
        except Exception, e:
            if isinstance(e, socket.error):
                if e[0] == 111:
                    s.write("ERROR: %s\n" % e[1])
            else:
                s.write("ERROR: %s\n" % e)
                s.write(format_exc())

        r = s.getvalue()
        if type(r) == str:
            r = r.replace("\n", "<br />")
        s.close()

        return r

    def index(self):
        return render(self.tpl)

(Server(8000) + Debugger(events=False) + Root()).run()

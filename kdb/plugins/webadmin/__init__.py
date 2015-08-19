import sys
from traceback import format_tb


from circuits.web.errors import httperror
from circuits.web.exceptions import NotFound
from circuits import handler, Event, Component
from circuits.web import Controller, Static

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from pathlib import Path


from kdb.plugin import BasePlugin


class render(Event):
    """render Event"""


class JinjaTemplate(object):

    def __init__(self, _name, **context):
        self._name = _name
        self.context = context

    @property
    def name(self):
        return self._name


class JinjaRenderer(Component):

    channel = "web"

    def init(self, path, defaults=None):
        self.path = path
        self.defaults = defaults or {}

        self.env = Environment(loader=FileSystemLoader(path))

    @handler("response", priority=1.0)
    def serialize_response_body(self, event, response):
        template = response.body
        if not isinstance(template, JinjaTemplate):
            return

        try:
            request = response.request

            try:
                tmpl = self.env.get_template("{0}.html".format(template.name))
            except TemplateNotFound:
                raise NotFound()

            ctx = self.defaults.copy()
            ctx.update({"request": request, "response": response, "uri": request.uri})

            ctx.update(template.context)

            response.body = tmpl.render(**ctx)
        except:
            event.stop()
            evalue, etype, etraceback = sys.exc_info()
            error = (evalue, etype, format_tb(etraceback))
            self.fire(httperror(request, response, 500, error=error))


class Root(Controller):

    def GET(self, *args, **kwargs):
        return JinjaTemplate("views/index")


class WebApp(Component):

    def init(self, defaults=None, prefix="/"):
        root = Path(__file__).resolve().parent
        templates = root.joinpath("templates")
        static = root.joinpath("static")

        JinjaRenderer(str(templates), defaults=(defaults or {})).register(self)

        Static(prefix, docroot=str(static)).register(self)
        Root(channel=prefix).register(self)


class WebAdminPlugin(BasePlugin):
    """Web Admin Plugin

    WIP: A Web Admin Interface
    """

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(WebAdminPlugin, self).init(*args, **kwargs)

        WebApp(prefix="/admin").register(self)

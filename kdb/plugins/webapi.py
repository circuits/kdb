from cgi import escape
from traceback import format_exc


from circuits.web import Controller
from circuits.protocols.irc import strip


from ..utils import log
from ..events import cmd
from ..bot import wrapvalue
from ..plugin import BasePlugin


class API(Controller):

    channel = "/api"

    def _process_request(self, command, *args):
        if command not in self.parent.bot.command:
            yield log("Unknown Command: {0:s}", command)
            return

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

    def GET(self, event, *args, **kwargs):
        req, res = event.args[:2]
        res.headers["Content-Type"] = "text/plain"

        args = iter(args)
        command = next(args, None)

        return self._process_request(command, *args)


class WebAPI(BasePlugin):
    """WebAPI Plugin

    A RESTful(ish) Web API plugin that allos posting
    and accessing commands and resources of the bot
    and other plugins as if you were communicationg
    over IRC or using the Web interface.

    Example(s)::

        curl -q -s -o - http://localhost:8000/api/commands
        Available Commands: ...

    There are no commands for this plugin.
    """

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(WebAPI, self).init(*args, **kwargs)

        API().register(self)

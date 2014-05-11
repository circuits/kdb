#!/usr/bin/env python


import pytest


from circuits import handler, Component
from circuits.protocols.irc import join


from kdb.core import Core
from kdb.plugins import greeting


class App(Component):

    def __init__(self):
        super(App, self).__init__()

        self.config = {
            "host": "localhost",
            "port": 6667,
            "nick": "kdb",
            "plugins": [
                "greeting"
            ],
        }

        self.data = []
        self.events = []

        self.core = Core(self.config).register(self)

    @handler(False)
    def reset(self):
        self.data = []
        self.events = []

    @handler(channel="*", priority=101.0)
    def _on_event(self, event, *args, **kwargs):
        self.events.append(event)


@pytest.fixture()
def app(request):
    app = App()

    while app:
        app.flush()

    app.reset()

    return app


def test_greeting(app):
    app.fire(join(("foo", "foo", "foobar.com"), "#foo"))
    while app:
        app.flush()

    events = iter(app.events)

    e = next(events)
    assert e.name == "join"
    assert e.args[0] == ("foo", "foo", "foobar.com")
    assert e.args[1] == "#foo"

    e = next(events)
    assert e.name == "command_PRIVMSG"
    assert e.args[0] == "#foo"
    assert e.args[1] in [
        default.format("foo")
        for default in greeting.DEFAULTS
    ]

    e = next(events)
    assert e.name == "command_RAW"
    assert e.args[0] in [
        "PRIVMSG #foo :{0:s}".format(x)
        for x in [
            default.format("foo")
            for default in greeting.DEFAULTS
        ]
    ]

    e = next(events)
    assert e.name == "write"
    assert e.args[0] in [
        "PRIVMSG #foo :{0:s}\r\n".format(x)
        for x in [
            default.format("foo")
            for default in greeting.DEFAULTS
        ]
    ]

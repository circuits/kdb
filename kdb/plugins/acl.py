import re
from itertools import chain


from circuits import handler, Component


from ..events import cmd
from ..plugin import BasePlugin

from .basicauth import StateManager


def read_config(config):
    groups, users = {}, {}

    if "acl.groups" not in config:
        return groups, users

    for k, v in config["acl.groups"].items():
        groups[k] = map(re.compile, v)

    if "acl.users" not in config:
        return groups, users

    for k, v in config["acl.users"].items():
        users[k] = v[:]

    return groups, users


class Commands(Component):

    channel = "commands"

    @handler()
    def on_command(self, event, *args, **kwargs):
        if not event.channels == (self.channel,):
            return

        if not isinstance(event, cmd):
            return

        source, target, args = args

        session = self.parent.state.whois(source)
        user = session.username if session is not None else "*"

        gs = (self.parent.groups.get(g, []) for g in self.parent.users.get(user, []))
        if not any(g.match(event.name) for g in chain(*gs)):
            event.stop()
            return "Access Denied!"


class ACL(BasePlugin):
    """ACL Plugin

    A simple ACL Plugin to allow or deny access
    to certain classes of commands based on patterns
    and memberships.

    Depends on: basicauth

    See: commands acl
    """

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(ACL, self).init(*args, **kwargs)

        self.data.init(
            {
                "acl": {
                    "sessions": {},
                }
            }
        )

        data = self.data["acl"]

        self.groups, self.users = read_config(self.config)

        Commands().register(self)
        self.state = StateManager(data).register(self)

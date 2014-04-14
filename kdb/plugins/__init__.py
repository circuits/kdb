# Module:   __init__
# Date:     30 June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Plugins

Default kdb plugins
"""


from __future__ import print_function


import sys
from traceback import format_exc
from inspect import getmembers, isclass


from pymills.utils import safe__import__


from circuits.tools import kill
from circuits import Event, Component

from cidict import cidict


from ..utils import log
from ..plugin import BasePlugin


DEFAULTS = ["core", "channels", "help", "irc"]


class load(Event):
    """load Event"""


class query(Event):
    """query Event"""


class unload(Event):
    """unload Event"""


class Plugins(Component):

    channel = "plugins"

    def init(self, init_args=None, init_kwargs=None):
        self.init_args = init_args or tuple()
        self.init_kwargs = init_kwargs or dict()

        self.plugins = cidict()

    def query(self, name=None):
        if name is None:
            return self.plugins
        else:
            return self.plugins.get(name, None)

    def load(self, name, package=__package__):
        if name in self.plugins:
            msg = log("Not loading already loaded plugin: {0:s}", name)
            return msg

        try:
            fqplugin = "{0:s}.{1:s}".format(package, name)
            if fqplugin in sys.modules:
                reload(sys.modules[fqplugin])

            m = safe__import__(name, globals(), locals(), package)

            p1 = lambda x: isclass(x) and issubclass(x, BasePlugin)
            p2 = lambda x: x is not BasePlugin
            predicate = lambda x: p1(x) and p2(x)
            plugins = getmembers(m, predicate)

            for name, Plugin in plugins:
                instance = Plugin(*self.init_args, **self.init_kwargs)
                instance.register(self)
                log(
                    "Registered Component: {0:s}",
                    instance
                )
                if name not in self.plugins:
                    self.plugins[name] = set()
                self.plugins[name].add(instance)

            msg = log("Loaded plugin: {0:s}", name)
            return msg
        except Exception, e:
            msg = log(
                "Could not load plugin: {0:s} Error: {1:s}",
                name,
                e
            )
            log(format_exc())
            return msg

    def unload(self, name):
        if name in self.plugins:
            instances = self.plugins[name]
            for instance in instances:
                kill(instance)
                log("Unregistered Component: {0:s}", instance)
                if hasattr(instance, "cleanup"):
                    instance.cleanup()
                    log("Cleaned up Component: {0:s}", instance)
            del self.plugins[name]

            msg = log("Unloaded plugin: {0:s}", name)
        else:
            msg = log("Not unloading unloaded plugin: {0:s}", name)

        return msg

# Plugin:   hello
# Date:     8th April 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""hello Plugin"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from circuits import Component


from kdb.plugin import BasePlugin


class Commands(Component):

    channel = "commands"

    def hello(self, source, target, message):
        return "Hello {0:s}".format(message or "World!")


class Hello(BasePlugin):
    """Hello Plugin"""

    def init(self, *args, **kwargs):
        super(Test, self).init(*args, **kwargs)

        Commands().register(self)

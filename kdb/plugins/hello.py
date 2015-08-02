from circuits import Component


from ..plugin import BasePlugin


class Commands(Component):

    channel = "commands"

    def hello(self, source, target, args):
        """Say Hello.

        Syntax: HELLO [<message>]
        """

        if not args:
            message = "World!"
        else:
            message = args

        return "Hello {0:s}".format(message or "World!")

    def say(self, source, target, args):
        """Say.

        Syntax: SAY <message>
        """

        if not args:
            return "No message specified."

        return args


class Hello(BasePlugin):
    """Hello Plugin

    An example of the simplest possible plugin.

    See: command hello
    """

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(Hello, self).init(*args, **kwargs)

        Commands().register(self)

from circuits import Component

from pymills.misc import beat


from ..plugin import BasePlugin


class Commands(Component):

    channel = "commands"

    def beat(self, source, target, args):
        """Display the current Swatch Time (Internet Time).

        Syntax: BEAT
        """

        return "@{0:0.2f}".format(beat())

    def itime(self, source, target, args):
        """Synonym, of BEAT

        See: BEAT
        """

        return self.beat(source, target, args)


class Swatch(BasePlugin):
    """Swatch Time plugin

    Provides commands to display Internet Time or Swatch Time.
    See: commands swatch
    """

    __version__ = "0.0.3"
    __author__ = "James Mills prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(Swatch, self).init(*args, **kwargs)

        Commands().register(self)

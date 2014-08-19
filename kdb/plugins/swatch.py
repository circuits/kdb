# Plugin:   swatch
# Date:     19th December 2006
# Author:   James Mills prologic at shortcircuit dot net dot au


"""Swatch Time

This plugin provides to the user a command that
can be used to display the current Swatch Time or
Internet Time or Beat.
"""


__version__ = "0.0.3"
__author__ = "James Mills prologic at shortcircuit dot net dot au"


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

    def init(self, *args, **kwargs):
        super(Swatch, self).init(*args, **kwargs)

        Commands().register(self)

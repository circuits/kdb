# Plugin:   eval
# Date:     30th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Expression Evaluation

This plugin provides a command to evaluate python expressions
and can be used as a simple way of performing calculations.
"""


__version__ = "0.0.3"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from circuits import Component

from simpleeval import simple_eval


from ..utils import log
from ..plugin import BasePlugin


class Commands(Component):

    channel = "commands"

    def eval(self, source, target, args):
        """Evaluates the given expression and displays the result.

        Syntax: EVAL [<expr> ...]
        """

        if not args:
            return "No expression given."

        expression = args

        try:
            return str(simple_eval(expression))
        except Exception, error:
            return log("ERROR: {0:s}", error)

    def sum(self, source, target, args):
        """Sum a list of numbers

        Syntax: SUM [<n1>, <n2>, <n3>, ...]
        """

        args = args.split(" ")

        try:
            return sum((float(arg) for arg in args))
        except Exception as error:
            return log("ERROR: {0:s}", error)


class Eval(BasePlugin):
    """Evalulation (expression) plugin

    Provides a command to evaluate python expressions and
    can be used as a simple way of calculating expressions.

    See: HELP eval
    """

    def init(self, *args, **kwargs):
        super(Eval, self).init(*args, **kwargs)

        Commands().register(self)

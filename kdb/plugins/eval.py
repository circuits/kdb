# Module:   eval
# Date:     30th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Expression Evaluation 

This plugin provides a command to evaluate python expressions
and can be used as a simple way of performing calculations.
"""

__version__ = "0.0.3"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from kdb.plugin import BasePlugin

class Eval(BasePlugin):

    """Evalulation (expression) plugin

    Provides a command to evaluate python expressions and
    can be used as a simple way of calculating expressions.

    See: help eval
    """

    def cmdEVAL(self, source, target, s):
        """Evaluates the given expression and displays the result.

        Syntax: EVAL <expr>
        """

        try:
            msg = str(eval(s)).split("\n")
        except Exception, e:
            msg = ["ERROR: (%s) %s" % (e.__class__.__name__, e)]

        return msg

    def cmdSUM(self, source, target, s, sep=None):
        """Sum a list of numbers

        Syntax: SUM <list> [<separator>]
        """

        try:
            if sep:
                return sum([int(x.strip()) for x in s.split(sep)])
            else:
                return sum([int(x.strip()) for x in s.split()])
        except Exception, error:
            return "ERROR: %s" % error

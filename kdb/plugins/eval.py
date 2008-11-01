# Filename: eval.py
# Module:	eval
# Date:		30th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Expression Evaluation 

This plugin provides a command to evaluate python expressions
and can be used as a simple way of performing calculations.
"""

__ver__ = "0.0.2"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from rexec import RExec

from kdb.plugin import BasePlugin

class Eval(BasePlugin):

	"""Evalulation (expression) plugin

	Provides a command to evaluate python expressions and
	can be used as a simple way of calculating expressions.

	See: help eval
	"""

	def __init__(self, *args, **kwargs):
		super(Ai, self).__init__(*args, **kwargs)

		self.rexec = RExec()

	def cmdEVAL(self, source, s):
		"""Evaluates the given expression and displays the result.

		Syntax: EVAL <expr>
		"""

		try:
			msg = str(self.rexec.r_eval(s)).split("\n")
		except Exception, e:
			msg = ["ERROR: (%s) %s" % (e.__class__.__name__, e)]

		return msg

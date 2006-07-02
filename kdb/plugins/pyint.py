# Filename: pyint.py
# Module:	pyint
# Date:		30th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Python Interpreter

This plugin provides two commands that allow the user
to execute python statements and evaluate python expressions.
These are EXEC and EVAL respectively. Execution is
performed in a restricted environment provided by the
rexec module.
"""

__ver__ = "0.0.1"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

from rexec import RExec
from traceback import format_exc

from kdb.plugin import BasePlugin

class Pyint(BasePlugin):
	"Python Interpreter"

	def __init__(self, event, bot, env):
		BasePlugin.__init__(self, event, bot, env)

		self.rexec = RExec()

	def cmdEXEC(self, source, code):
		"""Execute the given code
		
		Syntax: EXEC <code>
		"""

		self.rexec.r_exec(code)
	
	def cmdEVAL(self, source, code):
		"""Evaluate the given code displaying the result
		
		Syntax: EVAL <code>
		"""

		try:
			msg = str(
					self.rexec.r_eval(code)).split("\n")
		except Exception, e:
			msg = ["ERROR: %s" % e] + format_exc().split("\n")

		return msg

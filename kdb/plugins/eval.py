# Filename: eval.py
# Module:	eval
# Date:		30th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Expression Evaluation 

This plugin provides a command to evaluate python expressions
and can be used as a simple way of performing calculations.
"""

__ver__ = "0.0.4"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import os
import threading
from time import sleep
from rexec import RExec
from popen2 import popen2

from pymills.utils import daemonize
from pymills.event import listener, Event, Worker

from kdb.plugin import BasePlugin

class EvalResultEvent(Event):

	def __init__(self, target, msg):
		Event.__init__(self, target, msg)

class EvalTask(Worker):

	def __init__(self, event, target, s):
		Worker.__init__(self, event)

		self.target = target
		self.s = s
		self.rexec = RExec()
		self._pid = None
	
	def run(self):
		try:
			code = """
import sys
from rexec import RExec
lines = str(RExec().r_eval(" ".join(sys.argv[1:]))).split("\n")
for line in lines:
	print line
"""
			stdout, stdin = popen2("/usr/bin/python -")
			stdin.write(code)
			msg = []
			for line in stdout:
				msg.append(line)
			stdin.close()
			stdout.close()
		except Exception, e:
			msg = ["ERROR: %s" % str(e)]
		self.event.push(
				EvalResultEvent(self.target, msg),
				"evalresult")
		self.stop()

def new_eval_task(*args, **kwargs):
	class NewEvalTask(EvalTask):
		pass
	return NewEvalTask(*args, **kwargs)

class Eval(BasePlugin):

	"""Evalulation (expression) plugin

	Provides a command to evaluate python expressions and
	can be used as a simple way of calculating expressions.

	See: help eval
	"""

	def __init__(self, event, bot, env):
		BasePlugin.__init__(self, event, bot, env)

		self._evalTasks = []

	def cleanup(self):
		for task in self._evalTasks:
			task.stop()
			os.kill(task._pid, signal.SIGTERM)

	@listener("evalresult")
	def onEVALRESULT(self, target, msg):
		for line in msg:
			self.bot.ircPRIVMSG(target, line)

	@listener("message")
	def onMESSAGE(self, source, target, message):

		addressed, target, message = self.isAddressed(
				source, target, message)

		if addressed:

			tokens = message.split(" ")

			if len(tokens) > 1:
				if tokens[0].upper() == "EVAL":

					if len(self._evalTasks) > 2:
						self.bot.irc.PRIVMSG(
								"Too many eval tasks in progress. "
								"Try again later...")
						return

					self._evalTasks.append(new_eval_task(
						self.event,
						target,
						" ".join(tokens[1:])))

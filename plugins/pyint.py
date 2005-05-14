# Filename: PyInt.py
# Module:   PyInt
# Date:     09th May 2005
# Author:   James Mills <prologic@shortcircuit.net.au>

"""PyInt Plugin

PyInt Plugin
"""

__name__ = "PyInt"
__desc__ = "Python Interpreter Plugin"
__ver__ = "0.0.1"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

import os
import pickle

from pymills import ircbot
from pymills.utils import Tokenizer

import conf

def init():
	pass

class Error(Exception):
	pass

class Pyint(ircbot.Plugin):
	"PyInt Plugin"

	def __init__(self, bot):
		ircbot.Plugin.__init__(self, bot)

		self.envGlobals = {}
		self.envLocals = {"__builtins__": {}}
		self.execList = []

		self._load()
	
	def __del__(self):
		self._save()
	
	def _load(self):
		file = conf.paths["data"] + '/env.data'
		if os.path.isfile(file):
			fd = open(file, 'r')
			self.envGlobals = pickle.load(fd)
			fd.close()

		file = conf.paths["data"] + '/exec.data'
		if os.path.isfile(file):
			fd = open(file, 'r')
			self.execList = pickle.load(fd)
			fd.close()
			for statement in self.execList:
				exec(statement, self.envGlobals, self.envLocals)

	def _save(self):
		fd = open(conf.paths["data"] + '/env.data', 'w')

		if self.envGlobals.has_key("__builtins__"):
			del self.envGlobals["__builtins__"]
	
		try:
			pickle.dump(self.envGlobals, fd)
		except Exception, e:
			raise Error("Cannot save envGlobals")

		fd.close()

		fd = open(conf.paths["data"] + '/exec.data', 'w')
		pickle.dump(self.execList, fd)
		fd.close()

	def getHelp(self, command):

		if command == None:
			help = "Commands: EVAL EXEC"
		elif command.upper() == "EVAL":
			help = "(Evaluates a Python Expression) - Syntax: EVAL <expression>"
		elif command.upper() == "EXEC":
			help = "(Executes a Python Statement) - Syntax: EXEC <statement>"
		else:
			help = "Invalid Command: %s" % command

		return help

	def doEVAL(self, target, expression):
		try:
			output = eval(expression, self.envGlobals, self.envLocals)
			self.bot.ircPRIVMSG(target, str(output))
		except Exception, e:
			self.bot.ircPRIVMSG(target, 'ERROR: ' + str(e))
	
	def doEXEC(self, target, statement):
		try:
			exec(statement, self.envGlobals, self.envLocals)
			self.execList.append(statement)
		except Exception, e:
			self.bot.ircPRIVMSG(target, 'ERROR: ' + str(e))

	def onMESSAGE(self, source, target, message):

		(addressed, target, message) = self.isAddressed(source, target, message)

		if addressed:

			tokens = Tokenizer(message)

			if tokens.peek().upper() == "EVAL":
				tokens.next()
				self.doEVAL(target, tokens.rest())
			elif tokens.peek().upper() == "EXEC":
				tokens.next()
				self.doEXEC(target, tokens.rest())

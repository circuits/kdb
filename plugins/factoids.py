# Filename: Factoids.py
# Module:   Factoids
# Date:     09th May 2005
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Factoids Plugin

Factoids Plugin
"""

__name__ = "Factoids"
__desc__ = "Factoids Plugin"
__ver__ = "0.0.1"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

import os
import re
import time
import string

from pymills import db
from pymills import ircbot
from pymills.utils import Tokenizer

import conf

database = "%s/facts.db" % conf.paths["data"]

schema = """
CREATE TABLE facts (
id INTEGER PRIMARY KEY,
who TEXT,
fact TEXT,
type TEXT,
value TEXT);
CREATE TABLE links (
x INTEGER,
y INTEGER);
"""

def init():
	if not os.path.isfile(database):
		db = db.SQLite(database)
		db.query(schema)

class Facts(db.SQLite):

	def __init__(self):
		db.SQLite.__init__(self, database)
	
	def _getFact(self, fact):
		fields = ["who", "fact", "type", "value"]
		table = "facts"
		condition = "fact LIKE \"%s\"" % fact
		limit = 1
		return self.select(fields, table, condition, limit)

	def _findFact(self, fact):
		fields = ["id"]
		table = "facts"
		condition = "fact LIKE \"%s\"" % fact
		limit = 1
		records = self.select(fields, table, condition, limit)
		return records.get("id")

	def _delFact(self, fact):
		id = self._findFact(fact)
		if not id == None:
			table = "facts"
			condition = "id=%d" % id
			self.delete(table, condition)
			return True
		else:
			return False
	
	def getCount(self):
		fields = ["COUNT(*) AS count"]
		table = "facts"
		records = self.select(fields, table)
		return records.get("count")

	def addFact(self, who, fact, type, value):
		fields = ["who", "fact", "type", "value"]
		table = "facts"
		values = [who, fact, type, value]
		self.insert(table, fields, values)

	def isFact(self, fact):
		return not self._findFact(fact) == None
	
	def listFacts(self, limit):
		fields = ["fact"]
		table = "facts"
		records = self.select(fields, table, None, limit)
		facts = []
		for record in records:
			facts.append(record["fact"])
		return facts
	
	def getFact(self, bot, source, fact):
		fact = self._getFact(fact)
		if not fact.empty():
			if fact.get("type") == "reply":
				msg = fact.get("value")
				msg = msg.replace('$nick', source[0])
				msg = msg.replace('$me', bot.getNick())
			else:
				if fact.get("who") == source[0]:
					msg = "you said that"
				else:
					msg = "%s said that" % fact.get("who")
				msg = "%s %s %s %s" % (msg, fact.get("fact"), fact.get("type"), fact.get("value"))
			return msg
		else:
			return "I don\'t know"

	def forgetFact(self, fact):
		if self._delFact(fact):
			msg = "I've forgotten %s" % fact
			return (True, msg)
		else:
			msg = "I don't know"
			return (False, msg)

	def learnFact(self, bot, source, message, overwrite=False):
	
		tokens = Tokenizer(message)
		who = source[0]

		if tokens.has("is"):
			type = "is"
		elif tokens.has("are"):
			type = "are"
		elif tokens.has("reply"):
			type = "reply"
		else:
			type = None

		if type in ["is", "are"]:
			i = tokens.index(type)
			fact = tokens.copy(0, i)
			value = tokens.copy(i + 1)

			if fact  == "":
				return (False, "")

			if self._findFact(fact) == None:
				self.addFact(who, fact, type, value)
				msg = "Okay"
				return (True, msg)
			else:
				if overwrite:
					self._delFact(fact)
					self.addFact(who, fact, type, value)
					msg = 'Okay'
					return (True, msg)
				else:
					msg = "But, %s" % self.getFact(bot, source, fact)
					return (True, msg)

		elif type == "reply":
			i = tokens.index(type)
			fact = tokens.copy(0, i)
			value = tokens.copy(i + 1)

			if fact  == "":
				return (False, "")

			if self._findFact(fact) == None:
				self.addFact(who, fact, type, value)
				msg = 'Okay'
				return (True, msg)
			else:
				if overwrite:
					self._delFact(fact)
					self.addFact(who, fact, type, value)
					msg = "Okay"
					return (True, msg)
				else:
					msg = "But, %s" % self.getFact(bot, source, fact)
					return (True, msg)
		else:
			return (False, "")

class Factoids(ircbot.Plugin):
	"Factoids Plugin"

	def __init__(self, bot):
		ircbot.Plugin.__init__(self, bot)

		self.facts = Facts()

		self.startTime = time.time()
		self.c = 0 # command count
		self.m = 0 # modifications count
		self.q = 0 # questions count

	def __del__(self):
		del self.facts

	def getHelp(self, command):

		if command == None:
			help = "Commands: STATUS, FORGET, NO, TELL"
		elif command.upper() == "STATUS":
			help = "(Display current status info) - Syntax: STATUS"
		elif command.upper() == "FORGET":
			help = "(Makes me forget about a fact) - Syntax: FORGET <fact>"
		elif command.upper() == "NO":
			help = "(Redefines a fact) - Syntax: NO <fact> <is|are> <value>"
		elif command.upper() == "TELL":
			help = "(Tells someone about a fact) - Syntax: TELL <nick> <fact>"
		else:
			help = "Invalid Command: %s" % command

		return help

	def doSTATUS(self, target):
		c, m, q = self.c, self.m, self.q
		f = self.facts.getCount()
		date = time.ctime(self.startTime)
		msg = "Since: %s (C: %d M: %d Q: %d) Factoids: %d" % (date, c, m, q, f)
		self.bot.ircPRIVMSG(target, msg)
	
	def doFORGET(self, source, target, fact):
		(result, msg) = self.facts.forgetFact(fact)
		if result:
			self.m += 1
			if source[0] == target:
				self.bot.ircPRIVMSG(target, msg)
			else:
				self.bot.ircPRIVMSG(target, source[0] + ', ' + msg)
	
	def doNO(self, source, target, message):
		(result, msg) = self.facts.learnFact(self.bot, source, message, overwrite=True)
		if result:
			self.m += 1
			if source[0] == target:
				self.bot.ircPRIVMSG(target, msg)
			else:
				self.bot.ircPRIVMSG(target, source[0] + ', ' + msg)
	
	def doTELL(self, source, target, who, fact):
		if self.facts.isFact(fact):
			msg = "%s wants me to tell you that %s" % (source[0], self.facts.getFact(fact))
			self.bot.ircPRIVMSG(who, msg)
		else:
			msg = "I don\'t know."
		self.bot.ircPRIVMSG(target, msg)
	
	def doLIST(self, source, target, num):
		try:
			limit = int(num)
			facts = self.facts.listFacts(limit)
			msg = "%s: %s" % (source[0], string.join(facts, ", "))
		except ValueError:
			msg = "Invalid number specified."
		self.bot.ircPRIVMSG(target, msg)

	def onMESSAGE(self, source, target, message):

		(addressed, target, message) = self.isAddressed(source, target, message)

		if addressed:
			tokens = Tokenizer(message)
			command = tokens.next()

			if command == '':
				msg = source[0] + ", Yes ?"
				self.bot.ircPRIVMSG(target, msg)
			elif command == 'status':
				self.c += 1
				self.doSTATUS(target)
			elif command == 'forget':
				self.c += 1
				fact = tokens.rest()
				self.doFORGET(source, target, fact)
			elif command == 'no':
				self.c += 1
				message = tokens.rest()
				self.doNO(source, target, message)
			elif command == 'list':
				self.c += 1
				num = tokens.next()
				self.doLIST(source, target, num)
			else:
				#m = re.search('(what \b(?:is|are)\b )?(.*) *?\?', message)
				m = re.search('(what \b(?:is|are)\b )?(.*) ?\?', message)
				if m == None:
					(result, msg) = self.facts.learnFact(self.bot, source, message)
					if result:
						self.m += 1
						if source[0] == target:
							self.bot.ircPRIVMSG(target, msg)
						else:
							self.bot.ircPRIVMSG(target, source[0] + ', ' + msg)
				else:
					self.q += 1
					tmp = m.group(2).strip()
					if source[0] == target:
						msg = self.facts.getFact(self.bot, source, tmp)
					else:
						msg = source[0] + ', ' + self.facts.getFact(self.bot, source, tmp)
					self.bot.ircPRIVMSG(target, msg)

		else:
			(result, msg) = self.facts.learnFact(self.bot, source, message)
			if result:
				self.m += 1

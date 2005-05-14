# Filename: Trivia.py
# Module:   Trivia
# Date:     09th May 2005
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Trivia Plugin

Trivia Plugin
"""

__name__ = "Trivia"
__desc__ = "Trivia Plugin"
__ver__ = "0.0.1"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

import os
import re
import time
import string

from pymills import db
from pymills import ircbot
from pymills.utils import  Tokenizer

import conf

database = "%s/trivia.db" % conf.paths["data"]

schema = """
CREATE TABLE categories (
id INTEGER PRIMARY KEY,
category TEXT);
CREATE TABLE questions (
id INTEGER PRIMARY KEY,
category INTEGER,
question TEXT);
CREATE TABLE answers (
id INTEGER PRIMARY KEY,
answer TEXT);
CREATE TABLE links (
question INTEGER,
answer INTEGER);
CREATE TABLE scores (
id INTEGER PRIMARY KEY,
nick TEXT,
score INTEGER);
"""

def init():
	if not os.path.isfile(database):
		db = db.SQLite(database)
		db.query(schema)

class TriviaDB(db.SQLite):

	def __init__(self):
		db.SQLite.__init__(self, database)
	
	def addCategory(self, category):
		fields = ["category"]
		table = "categories"
		values = [
			"\"%s\"" % category]
		self.insert(table, fields, values)

	def addQuestion(self, category, question):
		fields = ["category", "question"]
		table = "questions"
		values = [
			"%d" % category,
			"\"%s\"" % question]
		self.insert(table, fields, values)

	def addAnswer(self, answer):
		fields = ["answer"]
		table = "answers"
		values = [
			"\"%s\"" % answer]
		self.insert(table, fields, values)

	def addLink(self, question, answer):
		fields = ["question", "answer"]
		table = "links"
		values = [
			"%d" % question,
			"%d" % answer]
		self.insert(table, fields, values)

	def findCategory(self, category):
		fields = ["id"]
		table = "categories"
		condition = "category LIKE \"%s\"" % category
		limit = 1
		return self.select(fields, table, condition, limit)

	def findQuestion(self, question):
		fields = ["id"]
		table = "questions"
		condition = "question LIKE \"%s\"" % question
		limit = 1
		return self.select(fields, table, condition, limit)

	def findAnswer(self, answer):
		fields = ["id"]
		table = "answers"
		condition = "answer LIKE \"%s\"" % answer
		limit = 1
		return self.select(fields, table, condition, limit)

	def getCategory(self, id):
		fields = ["category"]
		table = "categories"
		condition = "id=%d" % id
		return self.select(fields, table, condition)

	def getQuestion(self, id):
		fields = ["question"]
		table = "questions"
		condition = "id=%d" % id
		return self.select(fields, table, condition)

	def getAnswer(self, id):
		fields = ["answer"]
		table = "answers"
		condition = "id=%d" % id
		return self.select(fields, table, condition)

	def getCount(self, table):
		fields = ["COUNT(*) AS count"]
		records = self.select(fields, table)
		return records.get("count")

class Trivia(ircbot.Plugin):
	"Trivia Plugin"

	def __init__(self, bot):
		ircbot.Plugin.__init__(self, bot)

		self.triviadb = TriviaDB()
		self.running = False
		self.question = None

	def getHelp(self, command):

		if command == None:
			help = "Commands: START, STOP, STATS, SCORES, ADD, DEL"
		elif command.upper() == "START":
			help = "(Start Trivia) - Syntax: START"
		elif command.upper() == "STOP":
			help = "(Stop Trivia) - Syntax: STOP"
		elif command.upper() == "STATS":
			help = "(Displa Stats) - Syntax: STATS"
		elif command.upper() == "SCORES":
			help = "(Display Scores) - Syntax: SCORES [<nick1>, <nick2>, ...]"
		elif command.upper() == "ADD":
			help = "(Add a Question) - Syntax: ADD <category>:<question>:<answer>"
		elif command.upper() == "DEL":
			help = "(Delete a Question) - Syntax: DEL <id>"
		else:
			help = "Invalid Command: %s" % command

		return help

	def doSTART(self, target):
		pass
	
	def doSTOP(self, target):
		pass
	
	def doSTATS(self, target):
		pass
	
	def doSCORES(self, target, data):
		pass
	
	def doADD(self, target, type, data):

		if type.upper() == "C":
			category = self.triviadb.findCategory(data)
			if category.empty():
				self.triviadb.addCategory(data)
				category = self.triviadb.findCategory(data)
				id = int(category.get("id"))
				msg = "Added category (id = %d): %s" % (id, data)
			else:
				id = int(category.get("id"))
				msg = "ERROR: Category %s already exists! (id = %d)" % (data, id)
		elif type.upper() == "Q":
			tokens = Tokenizer(data)
			category = #TODO: ...
			question = self.triviadb.findQuestion(data)
			if question.empty():
				self.triviadb.addQuestion(data)
				question = self.triviadb.findQuestion(data)
				id = int(question.get("id"))
				msg = "Added question (id = %d): %s" % (id, data)
			else:
				id = int(question.get("id"))
				msg = "ERROR: Question %s already exists! (id = %d)" % (data, id)
		elif type.upper() == "A":
			answer = self.triviadb.findAnswer(data)
			if answer.empty():
				self.triviadb.addAnswer(data)
				answer = self.triviadb.findAnswer(data)
				id = int(answer.get("id"))
				msg = "Added answer (id = %d): %s" % (id, data)
			else:
				id = int(answer.get("id"))
				msg = "ERROR: Answer %s already exists! (id = %d)" % (data, id)
		else:
			msg = "Invalid Type: %s" % type

		self.bot.ircPRIVMSG(target, msg)

	def doLINK(self, target, question, answer):
		pass
	
	def doDEL(self, target, id):
		pass
	
	def checkAnswer(self, source, target, data):
		pass
	
	def onMESSAGE(self, source, target, message):

		(addressed, target, message) = self.isAddressed(source, target, message)

		if addressed:
			tokens = Tokenizer(message)

			if tokens.peek().upper() == "TRIVIA":
				tokens.next()

				if tokens.peek().upper() == "START":
					tokens.next()
					self.doSTART(target)
				elif tokens.peek().upper() == "STOP":
					tokens.next()
					self.doSTOP(target)
				elif tokens.peek().upper() == "STATS":
					tokens.next()
					self.doSTATS(target)
				elif tokens.peek().upper() == "SCORES":
					tokens.next()
					self.doSTOP(target, tokens.rest())
				elif tokens.peek().upper() == "ADD":
					tokens.next()
					type = tokens.next()
					data = tokens.rest()
					self.doADD(target, type, data)
				elif tokens.peek().upper() == "LINK":
					tokens.next()
					question = tokens.next()
					answer = tokens.next()
					self.doLINK(target, question, answer)
				elif tokens.peek().upper() == "DEL":
					tokens.next()
					id = tokens.next()
					self.doDEL(target, id)
				else:
					self.bot.irvPRIVMSG(target, "Invalid Command: %s" % tokens.peek())
			else:
				if self.running:
					self.checkAnswer(source, target, message)
		else:
			if self.running:
				self.checkAnswer(source, target, message)

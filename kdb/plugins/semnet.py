# Filename: semnet.py
# Module:	semnet
# Date:		03th July 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Semantic Network

This plugin implements a semantic network (a kind of an AI)
that allows the user to create relationships between things
and ask questions.
"""

__ver__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import os
import re
import types
import string
import pickle

from pymills.semnet import *
from pymills.event import listener
from pymills.misc import strToBool

from kdb.plugin import BasePlugin

def tostr(x):

	t = type(x)
	if t == types.DictionaryType:
		return "{" + string.join(
				map(lambda k, d=x: tostr(k) + ": " + tostr(d[k]),
					x.keys()), ", ") + "}"

	if t == types.ListType:
		return "[" + string.join(
				map(lambda i: tostr(i), x),
				", ") + "]"

	return str(x)

class Semnet(BasePlugin):
	"Semantic Network"

	def __init__(self, event, bot, env):
		BasePlugin.__init__(self, event, bot, env)

		self.isa = GetIsA()
		self.exampleof = GetExampleOf()

		self.relations = {
				"isa": self.isa,
				"exampleOf": self.exampleof}
		self.entities = {}

		filename = os.path.join(self.env.path, "semnet.bin")
		if os.path.exists(filename):
			fp = open(filename, "rb")
			r, e = pickle.load(fp)
			self.relations.update(r)
			self.entities.update(e)
			fp.close()

	def cleanup(self):
		filename = os.path.join(self.env.path, "semnet.bin")
		fp = open(filename, "wb")
		pickle.dump((self.relations, self.entities), fp)
		fp.close()

	def cmdSEMNET(self, source):
		"""Display the current Semantic Network
		
		Syntax: SEMNET
		"""

		msg = [
				"Entities: %s" % ", ".join(self.entities.keys()),
				"Relations: %s" % ", ".join(self.relations.keys())
				]
		return msg

	def cmdE(self, source, name):
		"""Synonym, of ENTITY
		
		See: ENTITY
		"""

		return self.cmdENTITY(source, name)

	def cmdENTITY(self, source, name):
		"""Create a new entity
		
		Syntax: ENTITY <name>
		"""

		if not self.entities.has_key(name):
			self.entities[name] = Entity(name)
			return "Okay"
		else:
			return [
					"I already know something about %s" % name,
					tostr(self.entities[name])]

	def cmdD(self, source, name):
		"""Synonym, of DELETE
		
		See: DELETE
		"""

		return self.cmdDELETE(source, name)

	def cmdDELETE(self, source, name):
		"""Delete an existing entity
		
		Syntax: DELETE <name>
		"""

		if self.entities.has_key(name):
			del self.entities[name]
			return "Okay"
		else:
			return "I don't know anything about %s" % name

	def cmdR(self, source, name, transitive="yes",
			opposite=None):
		"""Synonym, of RELATION
		
		See: RELATION
		"""

		return self.cmdRELATION(source, name, transitive,
				opposite)

	def cmdRELATION(self, source, name, transitive="yes",
			opposite=None):
		"""Create a new relationship
		
		Syntax: RELATION <name> [<transitive>] [<opposite>]
		"""

		if opposite is None:
			self.relations[name] = Relation(
					name, strToBool(transitive))
		else:
			self.relations[name] = Relation(
					name, strToBool(transitive))
			self.relations[opposite] = Relation(
					opposite, strToBool(transitive),
					self.relations[name])

		return "Okay"

	@listener("message")
	def onMessage(self, source, target, message):

		addressed, target, message = self.isAddressed(
				source, target, message)

		if addressed:

			if type(target) == tuple:
				target = target[0]

			m = re.match(
					"^(?P<agent>[a-zA-Z0-9_]+) "
					"(?P<relation>[a-zA-Z0-9_]+) ?\?",
					message)
			if m is not None:
				d = m.groupdict()
				if self.entities.has_key(d["agent"]) and \
						self.relations.has_key(d["relation"]):
					agent = self.entities[d["agent"]]
					relation = self.relations[d["relation"]]
					self.bot.ircPRIVMSG(
						target,
						tostr(agent.objects(relation)))
				else:
					self.bot.ircPRIVMSG(
						target, 
						"I don't understand.")
					if not self.entities.has_key(d["agent"]):
						self.bot.ircPRIVMSG(
							target,
							"What is a %s ?" % d["agent"])
					if not self.relations.has_key(d["relation"]):
						self.bot.ircPRIVMSG(
							target,
							"What does %s mean ?" % d["relation"])

				return

			m = re.match(
					"^(?P<agent>[a-zA-Z0-9_]+) "
					"(?P<relation>[a-zA-Z0-9_]+) "
					"(?P<object>[a-zA-Z0-9_]+) ?\?",
					message)
			if m is not None:
				d = m.groupdict()
				if self.entities.has_key(d["agent"]) and \
						self.relations.has_key(d["relation"]) and \
						self.entities.has_key(d["object"]):
					agent = self.entities[d["agent"]]
					relation = self.relations[d["relation"]]
					object = self.entities[d["object"]]

					if relation(agent, object):
						self.bot.ircPRIVMSG(target, "yes")
					else:
						self.bot.ircPRIVMSG(target, "no")
				else:
					self.bot.ircPRIVMSG(
						target, 
						"I don't understand.")
					if not self.entities.has_key(d["agent"]):
						self.bot.ircPRIVMSG(
							target,
							"What is a %s ?" % d["agent"])
					if not self.relations.has_key(d["relation"]):
						self.bot.ircPRIVMSG(
							target,
							"What does %s mean ?" % d["relation"])
					if not self.entities.has_key(d["object"]):
						self.bot.ircPRIVMSG(
							target,
							"What is a %s ?" % d["object"])

				return

			m = re.match(
					"^(?P<agent>[a-zA-Z0-9_]+) "
					"(?P<relation>[a-zA-Z0-9_]+) "
					"(?P<object>[a-zA-Z0-9_]+)",
					message)
			if m is not None:
				d = m.groupdict()
				if self.entities.has_key(d["agent"]) and \
						self.relations.has_key(d["relation"]) and \
						self.entities.has_key(d["object"]):
					agent = self.entities[d["agent"]]
					relation = self.relations[d["relation"]]
					object = self.entities[d["object"]]

					if relation(agent, object):
						self.bot.ircPRIVMSG(
								target,
								"I already knew that.")
					else:
						Fact(agent, relation, object)
						self.bot.ircPRIVMSG(target, "Okay")
				else:
					self.bot.ircPRIVMSG(
						target, 
						"I don't understand.")
					if not self.entities.has_key(d["agent"]):
						self.bot.ircPRIVMSG(
							target,
							"What is a %s ?" % d["agent"])
					if not self.relations.has_key(d["relation"]):
						self.bot.ircPRIVMSG(
							target,
							"What does %s mean ?" % d["relation"])
					if not self.entities.has_key(d["object"]):
						self.bot.ircPRIVMSG(
							target,
							"What is a %s ?" % d["object"])

				return
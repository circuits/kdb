# Filename: Factoids.py
# Module:   Factoids
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Factoids

Factoids module
"""

import Tokenizer
import data, Bot

class Fact:

	def __init__(self, source, target, bot):
		self.source = source
		self.target = target
		self.bot = bot
	
	def _get(self, subject):
		index = self.find(subject)
		if index > -1:
			return data.facts[index]
		else:
			return None
	
	def list(self, n):
		facts = []
		for fact in data.facts:
			facts.append(fact["subject"])
		if n < 0:
			return facts[n:]
		else:
			return facts[n:(n + 10)]
	
	def get(self, subject):
		fact = self._get(subject)
		if not fact == None:
			msg = ''
			if fact['type'] == 'reply':
				msg = fact['content']
				msg = msg.replace('$nick', self.source[0])
				msg = msg.replace('$me', self.bot.me["nick"])
				#msg = msg.replace('$commands', Bot.Bot.commands)
			else:
				if fact['who'] == self.source[0]:
					msg = msg + 'you said that '
				else:
					msg = msg + fact['who'] + ' said that '
				msg = msg + fact['subject'] + ' '
				msg = msg + fact['type'] + ' '
				msg = msg + fact['content']
			return msg
		else:
			return 'I don\'t know'

	def find(self, subject):
		for i in range(0, len(data.facts)):
			if data.facts[i]['subject'] == subject:
				return i
		return -1
	
	def forget(self, subject):
		if self.delete(subject):
			msg = 'I\'ve forgotten \'' + subject + '\''
			return (True, msg)
		else:
			msg = 'I don\'t know'
			return (False, msg)

	def delete(self, subject):
		i = self.find(subject)
		if i > -1:
			del data.facts[i]
			return True
		else:
			return False
	
	def add(self, type, who, subject, content):
		fact = {}
		fact['type'] = type
		fact['who'] = who
		fact['subject'] = subject
		fact['content'] = content
		data.facts.append(fact)

	def learn(self, message, overwrite = False):
	
		tokens = Tokenizer.Tokenizer(message)
		who = self.source[0]

		if tokens.has('is'):
			i = tokens.index('is')
			subject = tokens.copy(0, i)
			content = tokens.copy(i + 1)

			if subject  == '':
				return (False, '')

			if self._get(subject) == None:
				self.add('is', who, subject, content)
				msg = 'Okay'
				return (True, msg)
			else:
				if overwrite:
					self.delete(subject)
					self.add('is', who, subject, content)
					msg = 'Okay'
					return (True, msg)
				else:
					msg = 'But, ' + self.get(subject)
					return (True, msg)
		elif tokens.has('are'):
			i = tokens.index('are')
			subject = tokens.copy(0, i)
			content = tokens.copy(i + 1)

			if subject  == '':
				return (False, '')

			if self._get(subject) == None:
				self.add('are', who, subject, content)
				msg = 'Okay'
				return (True, msg)
			else:
				if overwrite:
					self.delete(subject)
					self.add('are', who, subject, content)
					msg = 'Okay'
					return (True, msg)
				else:
					msg = 'But, ' + self.get(subject)
					return (True, msg)
		elif tokens.has('reply'):
			i = tokens.index('reply')
			subject = tokens.copy(0, i)
			content = tokens.copy(i + 1)

			if subject  == '':
				return (False, '')

			if self._get(subject) == None:
				self.add('reply', who, subject, content)
				msg = 'Okay'
				return (True, msg)
			else:
				if overwrite:
					self.delete(subject)
					self.add('reply', who, subject, content)
					msg = 'Okay'
					return (True, msg)
				else:
					msg = 'But, ' + self.get(subject)
					return (True, msg)
		else:
			return (False, '')

#" vim: tabstop=3 nocindent autoindent

# Filename: Bot.py
# Module:   Bot
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Bot

Bot Class
"""

import re, time, socket, string
import IRC, Tokenizer, utils
import conf, data, Factoids, hosting

class Bot(IRC.Client):

	EAT_PLUGIN	= 0
	EAT_BOT		= 1
	EAT_ALL		= 2
	EAT_NONE		= 3

	# Commands

	def doEVAL(self, source, target, expression):
		try:
			output = eval(expression, data.envGlobals, data.envLocals)
			self.ircPRIVMSG(target, str(output))
		except Exception, e:
			self.ircPRIVMSG(target, 'ERROR: ' + str(e))
	
	def doEXEC(self, source, target, statement):
		try:
			exec(statement, data.envGlobals, data.envLocals)
			data.execList.append(statement)
		except Exception, e:
			self.ircPRIVMSG(target, 'ERROR: ' + str(e))

	def doQUIT(self, source, target):
		self.ircQUIT()

	def doNICK(self, source, target, nick):
		self.ircNICK(nick)
	
	def doUPTIME(self, source, target):
		uptime = utils.duration(time.time() - data.startTime)
		cpu = time.clock()
		msg = 'Uptime: ' + uptime + ' (CPU: ' + str(cpu) + ')'
		self.ircPRIVMSG(target, msg)
	
	def doSTATUS(self, source, target):
		c = data.getCount('commands')
		m = data.getCount('modifications')
		q = data.getCount('questions')
		f = len(data.facts)
		date = time.ctime(data.startTime)
		msg = 'Since: ' + date + ' ('
		msg = msg + 'C: ' + str(c) + ' '
		msg = msg + 'M: ' + str(m) + ' '
		msg = msg + 'Q: ' + str(q) + ') '
		msg = msg + 'Factoids: ' + str(f) + ' '
		self.ircPRIVMSG(target, msg)
	
	def doFORGET(self, source, target, subject):
		fact = Factoids.Fact(source, target, self)
		(result, msg) = fact.forget(subject)
		if result:
			data.incCount('modifications')
			if source[0] == target:
				self.ircPRIVMSG(target, msg)
			else:
				self.ircPRIVMSG(target, source[0] + ', ' + msg)
	
	def doNO(self, source, target, message):
		fact = Factoids.Fact(source, target, self)
		(result, msg) = fact.learn(message, True)
		if result:
			data.incCount('modifications')
			if source[0] == target:
				self.ircPRIVMSG(target, msg)
			else:
				self.ircPRIVMSG(target, source[0] + ', ' + msg)
	
	def doHOST(self, source, target, host):
		if re.search('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', host):
			if source[0] == target:
				msg = 'Hostname: ' + socket.gethostbyaddr(host)
			else:
				msg = source[0] + ', Hostname: ' + socket.gethostbyaddr(host)
		else:
			if source[0] == target:
				msg = 'IP: ' + socket.gethostbyname(host)
			else:
				msg = source[0] + ', IP: ' + socket.gethostbyname(host)
		self.ircPRIVMSG(target, msg)
	
	def doTELL(self, source, target, who, subject):
		fact = Factoids.Fact(source, target, self)
		if fact.find(subject) > -1:
			msg = source[0] + " wants me to tell you that "
			msg = msg + fact.get(subject)
			self.ircPRIVMSG(who, msg)
		else:
			msg = "I don\'t know."
		self.ircPRIVMSG(target, msg)
	
	def doLIST(self, source, target, num):
		try:
			n = int(num)
			fact = Factoids.Fact(source, target, self)
			facts = fact.list(n)
			msg = source[0] + ", " + string.join(facts, ", ")
		except ValueError:
			msg = "Invalid number specified."
		self.ircPRIVMSG(target, msg)

	def doHOSTING_PRICE(self, source, target, args):
		tokens = Tokenizer.Tokenizer(args)
		msg = ""
		space = 0
		transfer = 0
		discount = 0
		for i in range(0, tokens.count()):
			if i == 0:
				try:
					space = int(tokens.next())
				except ValueError, e:
					msg = "ERROR: Bad argument \"SPACE\" (" + int(i) + ")"
					break
			elif i == 1:
				try:
					transfer = int(tokens.next())
				except ValueError, e:
					msg = "ERROR: Bad argument \"transfer\" (" + int(i) + ")"
					break
			elif i == 2:
				try:
					discount = int(tokens.next())
				except ValueError, e:
					msg = "ERROR: Bad argument \"discount\" (" + int(i) + ")"
					break

		if not msg == None:
			price = hosting.hosting_price(space, transfer, discount)
			if price == None:
				msg = source[0] + ", " + "Not possible!"
			else:
				msg = source[0] + ", "
				msg = msg + "$ " + str(round(float(price), 2))
				msg = msg + " /month (AUD)"
				if discount > 0:
					msg = msg + " (Discount: " + str(discount) + "%)"

		self.ircPRIVMSG(target, msg)
	
	# Events

	def onCTCP(self, source, target, type, message):
	
		if type == "PING":
			self.ircCTCPREPLY(source[0], "PING", message)

	def onPING(self, server):
		self.ircPONG(server)

	def onMESSAGE(self, source, target, message):

		ref = False

		if target == self.me["nick"]:
			target = source[0]
			ref = True

		if target == self.me["nick"]:
			ref = True
		else:
			if len(message) > len(self.me["nick"]):
				if message[0:len(self.me["nick"])] == self.me["nick"]:
					ref = True
					i = len(self.me["nick"]) + 1
					if not i == len(message):
						while message[i] in [':', ',', ' ']:
							i = i + 1
							if i == len(message):
								break
					message = message[i:len(message)]

		if ref:
			tokens = Tokenizer.Tokenizer(message)
			command = tokens.next()

			if command == '':
				msg = source[0] + ", Yes ?"
				self.ircPRIVMSG(target, msg)
			elif command == 'eval':
				data.incCount('commands')
				expression = tokens.rest()
				self.doEVAL(source, target, expression)
			elif command  == 'exec':
				data.incCount('commands')
				statement = tokens.rest()
				self.doEXEC(source, target, statement)
			elif command == 'quit':
				data.incCount('commands')
				self.doQUIT(source, target)
			elif command == 'nick':
				data.incCount('commands')
				nick = tokens.next()
				self.doNICK(source, target, nick)
			elif command == 'uptime':
				data.incCount('commands')
				self.doUPTIME(source, target)
			elif command == 'status':
				data.incCount('commands')
				self.doSTATUS(source, target)
			elif command == 'forget':
				data.incCount('commands')
				subject = tokens.rest()
				self.doFORGET(source, target, subject)
			elif command == 'no':
				data.incCount('commands')
				message = tokens.rest()
				self.doNO(source, target, message)
			elif command == 'host':
				data.incCount('commands')
				host = tokens.rest()
				self.doHOST(source, target, host)
			elif command == 'tell':
				data.incCount('commands')
				who = tokens.next()
				subject = tokens.rest()
				self.doTELL(source, target, who, subject)
			elif command == 'list':
				data.incCount('commands')
				num = tokens.next()
				self.doLIST(source, target, num)
			elif command == 'hosting_price':
				data.incCount('commands')
				args = tokens.rest()
				self.doHOSTING_PRICE(source, target, args)
			else:
				fact = Factoids.Fact(source, target, self)

				#m = re.search('(what \b(?:is|are)\b )?(.*) *?\?', message)
				m = re.search('(what \b(?:is|are)\b )?(.*) ?\?', message)
				if m == None:
					(result, msg) = fact.learn(message)
					if result:
						data.incCount('modifications')
						if source[0] == target:
							self.ircPRIVMSG(target, msg)
						else:
							self.ircPRIVMSG(target, source[0] + ', ' + msg)
					if fact.find(message) > -1:
						tmp = message
						if source[0] == target:
							msg = fact.get(tmp)
						else:
							msg = source[0] + ', ' + fact.get(tmp)
						self.ircPRIVMSG(target, msg)
				else:
					data.incCount('questions')
					tmp = m.group(2).strip()
					if source[0] == target:
						msg = fact.get(tmp)
					else:
						msg = source[0] + ', ' + fact.get(tmp)
					self.ircPRIVMSG(target, msg)

		else:
			fact = Factoids.Fact(source, target, self)
			(result, msg) = fact.learn(message)
			if result:
				data.incCount('modifications')

#" vim: tabstop=3 nocindent autoindent

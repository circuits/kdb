# Filename: rss.py
# Module:	rss
# Date:		25th March 2007
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""RSS

This plugin provides RSS aggregation functionality to the
user allowing the user to set personal and public RSS feeds
to be retrieved at regular intervals and messages to them.
"""

__ver__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from time import time

import feedparser

from pymills.misc import strToBool
from pymills.timers import TickEvent
from pymills.event import listener, Event

from kdb.plugin import BasePlugin

class Feed(object):

	def __init__(self, url, target, interval=3600):
		self.url = url
		self.target = target
		self.interval = interval

		self.next = time() + (self.interval * 60)
		self.entries = {}
		self.title = ""
		self.link = ""
	
	def checkTime(self):
		if time() > self.next:
			self.next = time() + (self.interval * 60)
			return True
		else:
			return False
	
	def getItems(self):
		s = []

		d = feedparser.parse(self.url)

		s.append("RSS: %s (%s)" % (
			d.feed.title, d.feed.link))

		self.title = d.feed.title
		self.link = d.feed.link

		if not d.entries == self.entries:
			self.entries = d.entries
			for i, e in enumerate(d.entries[:3]):
				s.append(" %d. %s (%s)" % (
					(i + 1), e.title, e.link))
		else:
			return []

		return s
	
class RSS(BasePlugin):

	"""RSS Aggregator plugin

	Provides RSS aggregation functions allowing you to
	create public or private RSS feeds that are downlaoded
	at regular intervals and checked and display.
	See: commands rss
	"""

	def __init__(self, event, bot, env):
		BasePlugin.__init__(self, event, bot, env)

		self.entities = {}
		self.env.event.push(TickEvent(60), "rsstick")

	@listener("rsstick")
	def onRSSTICK(self, n):
		self.env.event.push(TickEvent(n), "rsstick")

		for entity in self.entities:
			for f in self.entities[entity]:
				if f.checkTime():
					for line in f.getItems():
						self.bot.ircPRIVMSG(f.target, line)
	
	def cmdRADD(self, source, url, interval="60"):
		"""Add a new RSS feed to be checked at the given interval.
		Intervan is in minutes.
		
		Syntax: RADD <url> [<interval>]
		"""

		try:
			interval = int(interval)
		except Exception, e:
			return "ERROR: Bad interval given '%s' --> %s" % (
					interval, str(e))

		if interval > 60:
			return "ERROR: Given interval '%s' is too big. " \
					"Interval is in minutes." % interval

		if type(source) == tuple:
			source = source[0]

		f = Feed(url, source, interval)
		if self.entities.has_key(source):
			self.entities[source].append(f)
		else:
			self.entities[source] = [f]
		
		return f.getItems()

	def cmdRDEL(self, source, n):
		"""Delete an RSS feed.
		
		Syntax: RDEL <n>
		"""

		if type(source) == tuple:
			source = source[0]

		if self.entities.has_key(source):

			try:
				n = int(n)
			except Exception, e:
				return "ERROR: Invalid feed no. given '%s' -> %s" % (
						n, str(e))

			if n > 0 and n < len(self.entities[source]):
				del self.entities[source][(n - 1)]
				msg = "Feed %d deleted." % n
			else:
				msg = "Given feed does not exist."
		else:
			msg = "No feeds to delete."

		return msg

	def cmdRLIST(self, source):
		"""List all active RSS feeds.
		
		Syntax: RLIST
		"""

		if type(source) == tuple:
			source = source[0]

		if self.entities.has_key(source):
			msg = ["RSS Feeds (%s):" % source]
			for i, f in enumerate(self.entities[source]):
				msg.append(" %d. %s (%s)" % (
					(i + 1), f.title, f.link))
		else:
			msg = "No feeds available."

		return msg

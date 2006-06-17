# Filename: env.py
# Module:	env
# Date:		15 June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id: __init__.py 202 2006-05-26 18:58:45Z prologic $

"""Environment Container

...
"""

import os

import default_config

VERSION = 1

class Environment:

	def __init__(self, path, create=False):
		self.path = os.path.abspath(os.path.expanduser(path))

		if create:
			self.create()
		else:
			self.verify()

		self.loadConfig()
		self.setupLog()
		self.loadDB()

		from pymills.event import EventManager
		self.event = EventManager()
		self.event.addListener(self.log.debug)

		from pymills.timers import Timers
		self.timers = Timers(self.event)

	def create(self):

		def createFile(filename, data=None):
			fd = open(filename, 'w')
			if data is not None:
				fd.write(data)
			fd.close()

		# Create the directory structure
		os.mkdir(self.path)
		os.mkdir(os.path.join(self.path, "db"))
		os.mkdir(os.path.join(self.path, "log"))
		os.mkdir(os.path.join(self.path, "conf"))
		os.mkdir(os.path.join(self.path, "plugins"))

		# Create a few files
		createFile(os.path.join(self.path, "VERSION"),
				"kdb Environment Version %d\n" % VERSION)
		createFile(os.path.join(self.path, "README"),
				"This directory contains a kdb environment.")

		# Setup the default configuration
		createFile(os.path.join(
			self.path, "conf", "kdb.ini"))
		default_config.createConfig(os.path.join(
			self.path, "conf", "kdb.ini"))
		self.loadConfig()

		# Create the database
		import default_db
		default_db.createDB(
				self.config.get("kdb", "database") % self.path)

	def verify(self):
		fd = open(os.path.join(self.path, "VERSION"), "r")
		try:
			version = fd.readlines()[0]
		except:
			version = ""
		fd.close()
		assert version.startswith("kdb Environment")
		self.version = int(
				version.split(
					"kdb Environment Version")[1].strip())

	def needsUpgrade(self):
		return VERSION > self.version

	def loadConfig(self):
		from pymills.config import Configuration
		self.config = Configuration(
				os.path.join(self.path, "conf", "kdb.ini"))
		for section, name, value in default_config.CONFIG:
			self.config.setdefault(section, name, value)
	
	def setupLog(self):
		from pymills.log import newLogger

		logType = self.config.get("logging", "type")
		logLevel = self.config.get("logging", "level")
		logFile = self.config.get("logging", "file")
		if not os.path.isabs(logFile):
			logFile = os.path.join(self.path, "log", logFile)
		logID = self.path

		self.log = newLogger(logType, logFile, logLevel, logID)
	
	def loadDB(self):
		import inspect
		from pymills.db import Connection

		from kdb import db

		dbConn = Connection(
				self.config.get("kdb", "database") % self.path)

		self.db = dict(
				[
					(n.lower(), v(dbConn))
					for n, v in inspect.getmembers(
						db, lambda x: inspect.isclass(x))
					]
				)

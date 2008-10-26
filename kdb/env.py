# Module:	env
# Date:		11th September 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""env - System Environment

System environment that acts as a container of objects in the system for
easier access by other parts of the system including plugins.
Every plugin is passed an instnace of this environment.
"""

import os

from pymills import config
from pymills.event import *
from pymills.env import Environment

import defaults
from db import (
		Databases,
		Load as LoadDatabases,
		Create as CreateDatabases)
from kdb import __name__ as systemName

class SystemEnvironment(Environment):

	version = 1
	name = systemName

	@listener("created")
	def onCREATED(self):
		for section in defaults.CONFIG:
			if not self.config.has_section(section):
				self.config.add_section(section)
			for option, value in defaults.CONFIG[section].iteritems():
				if type(value) == str:
					value = value % {"name": self.name}
				self.config.set(section, option, value)
		self.send(config.Save(), "save", "config")

		self.db = Databases(self)
		self.manager += self.db
		self.send(CreateDatabases(), "create", "db")

	@listener("loaded")
	def onLOADED(self):
		self.db = Databases(self)
		self.manager += self.db
		self.send(LoadDatabases(), "load", "db")

		self.errors = 0

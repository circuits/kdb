# Filename:	db.py
# Module:	db
# Date:		15th October 2005
# Author:	James Mills <prologic@shortcircuit.net.au>
# $Id: db.py 252 2006-06-09 05:36:26Z romster $

"""Database

This module implements the database needs.
"""

class Enum:

	def __init__(self, db):
		self._db = db
	
	def __contains__(self, (type, name)):
		db = self._db

		rows = db.do(
				"SELECT value "
				"FROM enum "
				"WHERE type=? AND name=?", type, name)

		return (not len(rows) == 0) and (rows[0].value >= 0)

	def __delitem__(self, (type, name)):
		db = self._db

		rows = db.do(
				"DELETE FROM enum "
				"WHERE type=? AND name=?", type, name)
	
	def __getitem__(self, (type, name)):
		db = self._db

		rows = db.do(
				"SELECT value "
				"FROM enum "
				"WHERE type=? AND name=?", type, name)

		if not len(rows) == 0:
			return rows[0].value
		else:
			return None

class System:

	def __init__(self, db):
		self._db = db
	def __contains__(self, name):
		db = self._db

		rows = db.do(
				"SELECT value "
				"FROM enum "
				"WHERE name=?", name)

		return not len(rows) == 0

	def __delitem__(self, name):
		db = self._db

		rows = db.do(
				"DELETE FROM enum "
				"WHERE name=?", name)
	
	def __getitem__(self, name):
		db = self._db

		rows = db.do(
				"SELECT value "
				"FROM enum "
				"WHERE name=?", name)

		if not len(rows) == 0:
			return rows[0].value
		else:
			return None

# Filename: db_default.py
# Module:	db_default
# Date:		9th June 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Default Database Schema

This module contains the default database schema used
to create the database if it doesn't exist.
"""

import sys
from pymills.db import Connection

__all__ = ["createDB", "VERSION"]

VERSION = 1

enum = """
CREATE TABLE enum (
type							TEXT,
name							TEXT,
value							TEXT,
UNIQUE(name, type)
);
"""

system = """
CREATE TABLE system (
name							TEXT PRIMARY KEY,
value						 	TEXT,
UNIQUE(name)
);
"""

systemData = [
		"""INSERT INTO "system" VALUES ("db_version", "%s")""" % VERSION
		]

TABLES = [enum, system]

DATA = systemData

def createDB(uri):
	db = Connection(uri)

	for table in TABLES:
		db.do(table)

	for line in DATA:
		db.do(line)
	
	db.commit()

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "Usage: python db_default.py <uri>"
		raise SystemExit, 1
	
	createDB(sys.argv[1])

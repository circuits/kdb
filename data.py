# Filename: data.py
# Module:   data
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""data

Data module
"""

import os, time
import conf, pickle

#Global Variables
startTime = time.time()
counts = {}

#Python Environment
#envGlobals = {"__builtins__": {}}
envGlobals = {}
envLocals = {"__builtins__": {}}
execList = []

#Factoids
facts = []

def incCount(count):
	global counts
	try:
		counts[count] = counts[count] + 1
	except KeyError:
		counts[count] = 1

def getCount(count):
	global counts
	try:
		return counts[count]
	except KeyError:
		return 0

def load():
	global envGlobals, envLocals, facts, execList

	file = conf.paths["data"] + '/env.data'
	if os.path.isfile(file):
		fd = open(file, 'r')
		envGlobals = pickle.load(fd)
		fd.close()

	file = conf.paths["data"] + '/fact.data'
	if os.path.isfile(file):
		fd = open(file, 'r')
		facts = pickle.load(fd)
		fd.close()

	file = conf.paths["data"] + '/exec.data'
	if os.path.isfile(file):
		fd = open(file, 'r')
		execList = pickle.load(fd)
		fd.close()
		for statement in execList:
			exec(statement, envGlobals, envLocals)

def save():
	global envGlobals, facts, execList

	fd = open(conf.paths["data"] + '/env.data', 'w')

	if envGlobals.has_key("__builtins__"):
		del envGlobals["__builtins__"]
	
	print envGlobals

	try:
		pickle.dump(envGlobals, fd)
	except Exception, e:
		print "ERROR: Cannot save Globals env"
		print str(e)

	fd.close()

	fd = open(conf.paths["data"] + '/fact.data', 'w')
	pickle.dump(facts, fd)
	fd.close()

	fd = open(conf.paths["data"] + '/exec.data', 'w')
	pickle.dump(execList, fd)
	fd.close()

#" vim: tabstop=3 nocindent autoindent

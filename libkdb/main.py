# Filename: Main.py
# Module:   Main
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Main

Main
"""

import os
import sys
import time
import signal
import traceback

from pymills import utils
from pymills import ircbot

import conf

def run(daemon, args):

	if args[0].upper() == "START":
		start(daemon)
	elif args[0].upper() == "STOP":
		stop()
	elif args[0].upper() == "RESTART":
		restart()
	elif args[0].upper() == "REHASH":
		rehash()
	else:
		print "ERROR: Invalid Command %s" % args[0]
		sys.exit(1)

def start(daemon = True):

	print "-- Starting kdb...\n"

	if daemon:
		logfile = conf.paths["logs"] + "/" + utils.getProgName() + '.log'
		utils.daemonize('/dev/null', logfile, logfile)

	pidfile = "%s/%s.pid" % (conf.paths["logs"], utils.getProgName())
	utils.writePID(pidfile)

	nick = conf.me["nick"]
	user = conf.me["user"]
	name = conf.me["name"]
	servers = conf.servers
	channels = conf.channels

	kdb = ircbot.Bot()
	kdb.loadPlugins(conf.paths["plugins"], conf.plugins)

	done = False
	errors = 0

	while not done:

		for server, port in servers:

			kdb.ircSERVER(server, port)
			kdb.ircUSER(user, "", server, name)
			kdb.ircNICK(nick)
			kdb.joinChannels(channels)

			try:
				kdb.run()
			except KeyboardInterrupt:
				kdb.stop()
				done = True
				break
			except SystemExit, status:
				done = True
				break
			except Exception, e:
				errors += 1
				print "ERROR: " + str(e)
				print "\nTraceBack follows:\n"
				traceback.print_exc()

		if errors > 0:
			print "ERROR: Too many errors! Aborting..."
			done = True
	
	print "No. errors: %d" % errors
	sys.exit(0)

def stop():
	try:
		pidfile = "%s/%s.pid" % (conf.paths["logs"], utils.getProgName())
		os.kill(int(open(pidfile).read()), signal.SIGTERM)
		print "-- kdb Stopped"
	except Exception, e:
		print "*** ERROR: Could not stop kdb..."
		print str(e)

def restart():
	stop()
	start()

def rehash():
	try:
		pidfile = "%s/%s.pid" % (conf.paths["logs"], utils.getProgName())
		os.kill(int(open(pidfile).read()), signal.SIGHUP)
		print "-- kdb Rehashed"
	except Exception, e:
		print "*** ERROR: Could not rehash kdb..."
		print str(e)

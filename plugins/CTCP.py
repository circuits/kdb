# Filename: CTCP.py
# Module:   CTCP
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""CTCP

CTCP Plugin
"""

import Bot
import Plugin

class CTCP(Plugin.Plugin):

	def __init__(self, bot):
		Plugin.__init__(bot)

		bot.hookEvent("onCTCP", self.onCTCP)
	
	#Events

	def onCTCP(self, source, target, type, message):
		print source
		print target
		print type
		print message

		return Bot.EAT_NONE

#" vim: tabstop=3 nocindent autoindent

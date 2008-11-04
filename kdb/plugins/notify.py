# Module:	notify
# Date:		30th June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Notify

This plugin listens for xmlrpc.notify and xmlrpc.scmupdate events
and displays them on the default xmlrpc channel.
"""

__ver__ = "0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from cPickle import loads

from circuits import listener

from kdb.plugin import BasePlugin

class Notify(BasePlugin):

	"""Notification plugin

	This doesn't have any user commands available.
	This provides notification support via XML-RPC and
	displays messages on the configured channel.

	Depends on: xmlrpc
	"""

	@listener("xmlrpc.scmupdate")
	def onSCMUPDATE(self, data):

		if self.env.config.has_option("xmlrpc", "channel"):
			channel = self.env.config.get("xmlrpc", "channel")
		else:
			channel = None

		if channel is not None:

			d = loads(data)
			files = d["files"]

			if len(files) > 3:
				d["files"] = "%s ... %d more files" % (
						" ".join(files[:3]),
						len(files) - 3)
			else:
				d["files"] = " ".join(files)

			msg = """\
%(project)s: 8%(committer)s 12%(rev)s \
%(logmsg)s (%(files)s)"""

			self.bot.ircPRIVMSG(channel, msg % d)

		return "Message sent to %s" % channel

	@listener("xmlrpc.notify")
	def onNOTIFY(self, source="unknown", message=""):

		print "onNOTIFY: ..."

		if self.env.config.has_option("xmlrpc", "channel"):
			channel = self.env.config.get("xmlrpc", "channel")
		else:
			channel = None

		if channel is not None:

			self.bot.ircPRIVMSG(channel,
					"Message from %s:" % source)

			for line in message.split("\n"):
				self.bot.ircPRIVMSG(channel, line)

		return "Message sent to %s" % channel

# Filename: autoid.py
# Module:	autoid
# Date:		03th July 2006
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Automatic Identification

This plugin automatically identifies the bot to services
if it's nick is registered. The configuration is
provided in the configuration file.
"""

__ver__ = "0.0.1"
__author__ = "James Mills <prologic@shortcircuit.net.au>"

import re

from pymills.event import listener

from kdb.plugin import BasePlugin

class AutoID(BasePlugin):
	"Automatic Identification"

	@listener("notice")
	def doLOGIN(self, event, source, target, message):
		"""Automatically login to pircsrv

		The password is stored in the config file.
		The service nickname is stored in the config file.
		The login pattern is stored in the config file.

		Example:
		[autoid]
		nickserv = pronick
		pattern = .*registered nick.*login
		command = LOGIN %s
		password = semaj2891
		"""

		if self.env.config.has_section("autoid"):

			if self.env.config.has_option(
					"autoid", "nickserv"):

				nickserv = self.env.config.get(
						"autoid", "nickserv")

				if source[0].lower() == nickserv.lower():

					if self.env.config.has_option(
							"autoid", "pattern"):

						pattern = self.env.config.get(
								"autoid", "pattern")

						if re.match(pattern, message):

							if self.env.config.has_option(
									"autoid", "command"):

								command = self.env.config.get(
										"autoid", "command")

								password = self.env.config.get(
										"autoid", "password")

								self.bot.ircPRIVMSG(
										nickserv,
										command % password)

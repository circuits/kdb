# Module:	trac
# Date:		01th July 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Trac

This plugin listeners for trac and wiki links and
tries to provide more information about them as well
as displaying their absolutel urls so users can easily
pop open the link in their browser.
"""

__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

from pymills.event import filter

from kdb.plugin import BasePlugin

class Trac(BasePlugin):
	"Trac"

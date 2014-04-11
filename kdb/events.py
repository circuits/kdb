# Module:   events
# Date:     6th April 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""events

This module defines events shared by various componetns of kdb.
"""

from circuits import Event


class cmd(Event):
    """cmd Event"""


class reconnect(Event):
    "Rrconnect Event"


class terminate(Event):
    """terminate Event"""

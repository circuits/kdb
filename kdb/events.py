"""events

This module defines events shared by various componetns of kdb.
"""


from circuits import Event


class cmd(Event):
    """cmd Event"""


class terminate(Event):
    """terminate Event"""

# Module:   travian
# Date:     21st July 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Travian

This plugin provides various commands to assist in playing the game
of Travian (http://www.travian.com.au).
"""

__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import types

from kdb.plugin import BasePlugin

from pymills.db import newDB

class Base(object):

    def __new__(cls, *args, **kwargs):
        self = object.__new__(cls)
        self.table = getattr(cls, "table", None)
        return self

    def __init__(self, db, table=None):
        super(Base, self).__init__()

        self.db = db
        self.table = self.table or table or self.__class__.__name__.lower()

    def __len__(self):
        SQL = "SELECT COUNT(*) AS n FROM %s" % self.table
        rows = self.db.do(SQL)
        if rows:
            return rows[0].n

    def __contains__(self, y):
        SQL = "SELECT COUNT(*) AS n FROM %s WHERE id=?" % self.table
        rows = self.db.do(SQL, y)
        if rows:
            return rows[0].n

    def __getitem__(self, y):
        SQL = "SELECT * FROM %s WHERE id=?" % self.table
        return self.db.do(SQL, y)

    def __delitem__(self, y):
        SQL = "DELETE FROM %s WHERE id=?" % self.table
        return self.db.do(SQL, y)

    def clear(self):
        SQL = "DELETE FROM %s" % self.table
        return self.db.do(SQL)

    def drop(self):
        SQL = "DROP %s" % self.table
        return self.db.do(SQL)

class World(Base):

    table = "x_world"

    def players(self, name):
        SQL = "SELECT * FROM %s WHERE player=?" % self.table
        rows = self.db.do(SQL, name)
        if rows:
            if len(rows) == 1:
                return rows[0]
            else:
                return (row for row in rows)

    def villages(self, name):
        SQL = "SELECT * FROM %s WHERE village=?" % self.table
        rows = self.db.do(SQL, name)
        if rows:
            if len(rows) == 1:
                return rows[0]
            else:
                return (row for row in rows)

class Travian(BasePlugin):

    """Travian plugin

    Provides various commands to aid in the playing of Travian.
    See: commands travian
    """

    def __init__(self, env):
        super(Travian, self).__init__(env)

        db = newDB("sqlite:///home/prologic/travian/s1.db")
        self.world = World(db)

    def cmdVILLAGES(self, source, name):
        """Display information about villages.

        Syntax: VILLAGES <name>
        """

        villages = self.world.villages(name)
        if villages:
            if type(villages) is types.GeneratorType:
                villages = list(villages)
                yield "%d villages found" % len(villages)
            else:
                villages = [villages]

            for village in villages:
                yield "%s %d (%d, %d) of %s (Alliance: %s)" % (
                        village.village,
                        village.population,
                        village.x, village.y,
                        village.player,
                        village.alliance)
        else:
            yield "No villages found by that name"

    def cmdPLAYER(self, source, name):
        """Display information about a player.

        Syntax: PLAYER <name>
        """

        players = self.world.players(name)
        if players:
            if type(players) is types.GeneratorType:
                players = list(players)
            else:
                players = [players]

            population = 0
            alliance = None
            villages = []
            for player in players:
                villages.append(player.village)
                population += player.population
                if not alliance:
                    alliance = player.alliance
            yield "%s with %d vilalges (%d), a member of '%s'" % (
                    name, len(villages), population, alliance)
            for i, village in enumerate(villages):
                yield "Village #%d: %s" % (i, village)
        else:
            yield "No players found by that name"

# Module:   travian
# Date:     21st July 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Travian

This plugin provides various commands to assist in playing the game
of Travian (http://www.travian.com.au).
"""

__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import os
import types
import pickle

from kdb.plugin import BasePlugin

from pymills.db import newDB
from pymills.datatypes import OrderedDict

TRIBES = "Natar", "Roman", "Teuton", "Gaul",

def loadTroops(filename):
    state = 0
    tribe = ""
    troops = OrderedDict()
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if state == 0:
                tribe = line
                troops[tribe] = OrderedDict()
                state = 1
            elif state == 1:
                if line:
                    troop, attr = line.split(":")
                    troops[tribe][troop] = attr.split()
                else:
                    tribe = ""
                    state = 0
    return troops

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
        SQL = "SELECT * FROM %s WHERE player LIKE ?" % self.table
        rows = self.db.do(SQL, name)
        if rows:
            if len(rows) == 1:
                return rows[0]
            else:
                return (row for row in rows)

    def villages(self, name):
        SQL = "SELECT * FROM %s WHERE village LIKE ?" % self.table
        rows = self.db.do(SQL, name)
        if rows:
            if len(rows) == 1:
                return rows[0]
            else:
                return (row for row in rows)

    def alliances(self, name):
        SQL = "SELECT * FROM %s WHERE alliance LIKE ?" % self.table
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

        uri = self.env.config.get("travian", "db", None)
        if uri:
            db = newDB(uri)
        else:
            raise TypeError("No db config found for travian")

        self.world = World(db)

        self.data = {}

        filename = os.path.join(self.env.path, "travian.bin")
        if os.path.exists(filename):
            fp = open(filename, "rb")
            self.data.update(pickle.load(fp))
            fp.close()

        troopfile = self.env.config.get("travian", "troopfile", None)
        if troopfile:
            self.troops = loadTroops(troopfile)
        else:
            raise TypeError("No troopfile config found for travian")

        self.enabled = True

    def _getPlayer(self, source):
        if type(source) is tuple:
            name = source[0]
        else:
            name = source

        players = self.world.players(name)
        if players:
            if type(players) is types.GeneratorType:
                players = list(players)
            else:
                players = [players]

            return players[0]
        else:
            return None

    def cleanup(self):
        filename = os.path.join(self.env.path, "travian.bin")
        fp = open(filename, "wb")
        pickle.dump(self.data, fp)
        fp.close()

    def cmdTRAVIANPARSER(self, source, target, option):
        """Turn Travian Parser on or off.
        
        Syntax: TRAVIANPARSER ON|OFF
        """

        opt = option.upper()
        if opt == "ON":
            if not self.enabled:
                self.enabled = True
                msg = "Travian Parser turned on."
            else:
                msg = "Travian Parser already on."
        elif opt == "OFF":
            if self.enabled:
                self.enabled = False
                msg = "Travian Parser turned off."
            else:
                msg = "Travian Parser not on."
        else:
            msg = "Unknown options: %s" % option

        return msg

    def cmdTROOP(self, source, target, name, tribe=None):
        """Display information about a particular troop.

        Syntax: TROOP <name> [<tribe>]
        """

        if type(source) is tuple:
            source = source[0]

        name = name.title()
        if tribe:
            tribe = tribe.title()
        else:
            player = self._getPlayer(source)
            if player:
                tribe = TRIBES[player.tid]

        troop = None

        if tribe and tribe in self.troops:
            troop = self.troops[tribe].get(name, None)
        else:
            for tribe, troops in self.troops.iteritems():
                if name in troops:
                    troop = troops[name]
                    break

        if troop:
            return "%s (%s): %s" % (name, tribe, " ".join(troop))
        else:
            return "No such troop or tribe found."

    def cmdTROOPS(self, source, target, tribe=None):
        """Display information about a tribe's troops.

        Syntax: TROOPS [<tribe>]
        """

        if not tribe:
            player = self._getPlayer(source)
            if player:
                tribe = TRIBES[player.tid]

        troops = self.troops.get(tribe, None)

        if troops:
            return "%s: %s" % (tribe, ", ".join(troops.keys()))
        else:
            return "No troops found for that tribe"

    def cmdCOST(self, source, target, name, n=None, tribe=None):
        """Display information about a particular troop's cost.

        Syntax: TROOP <name> [<n>] [<tribe>]
        """

        if type(source) is tuple:
            source = source[0]

        name = name.title()

        if n:
            try:
                n = int(n)
            except Exception, error:
                return "ERROR: %s" % error
        else:
            n = 1

        if tribe:
            tribe = tribe.title()
        else:
            player = self._getPlayer(source)
            if player:
                tribe = TRIBES[player.tid]

        troop = None

        if tribe and tribe in self.troops:
            troop = self.troops[tribe].get(name, None)
        else:
            for tribe, troops in self.troops.iteritems():
                if name in troops:
                    troop = troops[name]
                    break

        if troop:
            costs = [x.strip() for x in troop[3:7]]
            total = sum([int(x) for x in costs]) * n
            return "%dx %s (%s): %s (%d)" % (n, name, tribe,
                    " ".join(costs), total)
        else:
            return "No such troop or tribe found."

    def cmdVILLAGES(self, source, target, name):
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

    def cmdPLAYER(self, source, target, name=None):
        """Display information about a player.

        Syntax: PLAYER [<name>]
        """

        if not name:
            if type(source) is tuple:
                name = source[0]
            else:
                name = source

        players = self.world.players(name)
        if players:
            if type(players) is types.GeneratorType:
                players = list(players)
            else:
                players = [players]

            population = 0
            alliance = None
            villages = []
            tid = None
            for player in players:
                villages.append(player.village)
                population += player.population
                if not tid:
                    tid = player.tid
                if not alliance:
                    alliance = player.alliance

            tribe = TRIBES[tid]

            yield "%s (%s) with %d villages (%d), a member of '%s'" % (
                    name, tribe, len(villages), population, alliance)

            for i, village in enumerate(villages):
                yield "Village #%d: %s" % (i, village)
        else:
            yield "No players found by that name"

    def cmdALLIANCE(self, source, target, name):
        """Display information about an alliance.

        Syntax: ALLIANCE <name>
        """

        alliances = self.world.alliances(name)
        if alliances:
            if type(alliances) is types.GeneratorType:
                alliances = list(alliances)
                villages = len(alliances)
            else:
                alliances = [alliances]
                villages = 1

            population = 0
            members = set()

            for alliance in alliances:
                population += alliance.population
                members.add(alliance.player)

            yield "Alliance '%s': population=%d members=%d villages=%d" % (
                    name, population, len(members), villages)
        else:
            yield "No alliance found by that name"

    def message(self, source, target, message):

        addressed, target, message = self.isAddressed(
                source, target, message)

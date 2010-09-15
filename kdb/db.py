# Module:   db
# Date:     11th September 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""db - Database Module

...
"""

import os
import datetime
from copy import copy
from inspect import getmodule, getmembers

from buzhug import Base

from circuits import handler, Event, Component

###
### Base Database
###

class Database(Base):

    def __init__(self, path="db"):
        basename = self.__class__.__name__
        super(Database, self).__init__(basename, path)
        self.set_string_format(unicode, "utf-8")

    def create(self, **kwargs):
        return Base.create(self, *self.fields, **kwargs)

###
### Databases
###

class Enum(Database):
    fields = (
            ("type", str),
            ("name", str),
            ("value", str))

class Users(Database):
    fields = (
            ("username", str),
            ("password", str))

DEFAULTS = [
    ("users", [
        ("admin", "admin")
    ])
]

###
### Events
###

class Create(Event):
    """Create(Event) -> Create Event"""

class Load(Event):
    """Load(Event) -> Load Event"""

class Save(Event):
    """Save(Event) -> Save Event"""

###
### Components
###

class Databases(Component):

    channel = "db"

    def __init__(self, env):
        super(Databases, self).__init__()

        self.env = env

        self.enum = Enum(os.path.join(self.env.path, "db"))
        self.users = Users(os.path.join(self.env.path, "db"))

        self.dbs = [x for x in getmembers(self) if isinstance(x[1], Database)]

    @handler("create")
    def onCREATE(self):
        for db in (db[1] for db in self.dbs):
            db.create()

        for name, data in DEFAULTS:
            db = getattr(self, name)
            for values in data:
                x = []
                for v in values:
                    if type(v) == tuple:
                        x.append(getattr(self, v[0])[v[1]])
                    else:
                        x.append(v)
                db.insert(*x)
            db.commit()

    @handler("load")
    def onLOAD(self):
        for db in (db[1] for db in self.dbs):
            db.open()

    @handler("save")
    def onSAVE(self):
        for db in (db[1] for db in self.dbs):
            db.commit()

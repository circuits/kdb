# Module:   dbm
# Date:     24th July 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""DataBase Manager

...
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from circuits import handler, BaseComponent, Event

metadata = MetaData()
Base = declarative_base(metadata=metadata)

class DatabaseLoaded(Event):
    """Database Loaded Event"""

class DatabaseManager(BaseComponent):

    def __init__(self, dburi, echo=False, convert_unicode=True):
        super(DatabaseManager, self).__init__()

        self.metadata = metadata

        self.engine = create_engine(dburi,
            echo=echo,
            convert_unicode=convert_unicode,
        )

        self.session = scoped_session(
            sessionmaker(
                bind=self.engine,
                autoflush=True,
                autocommit=False,
            )
        )

    @handler("started", priority=1.0, target="*")
    def _on_started(self, component, mode):
        self.metadata.create_all(self.engine)
        self.push(DatabaseLoaded())

    @handler("stopped", target="*")
    def _on_stopped(self, component):
        self.session.flush()
        self.session.commit()
        self.session.close()

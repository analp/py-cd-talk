"""
Storage-related classes. Provides a default storage, backed by a SQL database.
"""
# pylint: disable=invalid-name,no-value-for-parameter

import enum
import os

import sqlalchemy as sa
from zope.interface import implementer

from ensign._interfaces import IStorage


class FlagTypes(enum.Enum):
    """
    Enumeration with all the possible flag types available.
    """

    BINARY = "binary"


@implementer(IStorage)
class SQLStorage:
    """
    SQL-backed flag storage.
    """

    engine = None
    connection = None
    metadata = sa.MetaData()

    flags = sa.Table(
        "flags", metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Unicode(64), nullable=False, unique=True),
        sa.Column("type", sa.Enum(FlagTypes), nullable=False),

        sa.Column("value_binary", sa.Boolean),

        sa.Column("label", sa.Unicode(256)),
        sa.Column("description", sa.UnicodeText),
        sa.Column("tags", sa.UnicodeText),
        sa.Column("used", sa.DateTime),
    )

    def init_db(self):
        """
        Initialise the database connection.
        To be called once per session.
        """

        self.engine = sa.create_engine(
            os.environ.get(
                "FLAGS_DB",
                "postgresql+psycopg2cffi:///flags",
            ),
        )
        self.metadata.create_all(self.engine)
        self.connection = self.engine.connect()

    def create(self, name, flagtype, **kwargs):
        """
        Create a new flag of the give type.
        """

        query = self.flags.insert().values(name=name, type=flagtype, **kwargs)
        self.connection.execute(query)

    def load(self, name):
        """
        Load a flag's value given its name. Updates the last used date.
        """

        with self.connection.begin():
            query = sa.select([self.flags.c.value_binary]).\
                where(self.flags.c.name == name)
            data = self.connection.execute(query).fetchone()
            query = self.flags.update().\
                where(self.flags.c.name == name).\
                values(used=sa.func.now())
            self.connection.execute(query)
            return data["value_binary"]

    def store(self, name, value):
        """
        Store a new value for a flag, given its name.
        """

        query = self.flags.update().\
            where(self.flags.c.name == name).\
            values(value_binary=value)
        self.connection.execute(query)

    def used(self, name):
        """
        Return a flag's last used date.
        """

        query = sa.select([self.flags.c.used]).\
            where(self.flags.c.name == name)
        return self.connection.execute(query).fetchone()["value_binary"]


DefaultStorage = SQLStorage()

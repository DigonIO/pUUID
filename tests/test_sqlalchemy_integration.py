from typing import Generator, Literal

import pytest
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.event import listen
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from puuid import PUUID, SqlPUUID

################################################################################
#### Types & Fixtures
################################################################################


class BaseORM(DeclarativeBase): ...


class UserUUID(PUUID[Literal["user"]]):
    _prefix = "user"


class UserORM(BaseORM):
    __tablename__ = "item_table"

    id: Mapped[UserUUID] = mapped_column(
        SqlPUUID(UserUUID),
        primary_key=True,
        default=UserUUID.factory,
    )


class AddressUUID(PUUID[Literal["address"]]):
    _prefix = "address"


class AddressORM(BaseORM):
    __tablename__ = "address_table"

    id: Mapped[AddressUUID] = mapped_column(
        SqlPUUID(AddressUUID, prefix_length=7),
        primary_key=True,
        default=AddressUUID.factory,
    )


@pytest.fixture()
def engine() -> Generator[Engine, None, None]:

    url = "sqlite:///:memory:"
    engine = create_engine(url, future=True)
    listen(engine, "connect", set_sqlite_pragma)

    BaseORM.metadata.create_all(engine)
    yield engine
    BaseORM.metadata.drop_all(engine)
    engine.dispose()


from sqlite3 import Connection

from sqlalchemy.pool.base import (
    _ConnectionRecord,
)  # pyright: ignore[reportPrivateUsage]

################################################################################
#### Tests
################################################################################


def test_success() -> None: ...


################################################################################
#### Util
################################################################################


# https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support
def set_sqlite_pragma(
    dbapi_connection: Connection, _connection_record: _ConnectionRecord
) -> None:
    """
    Enable foreign key constraints for SQLite connections.

    This function ensures that SQLite foreign key constraints are enabled.

    Notes
    -----
    SQLite's foreign key support is disabled by default and requires explicit
    enabling. The sqlite driver will not set PRAGMA foreign_keys if
    autocommit=False, which is why this function temporarily enables it.

    References
    ----------
    - SQLAlchemy SQLite Foreign Key Support:
      https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support

    Examples
    --------
    >>> from sqlalchemy import create_engine
    >>> from sqlalchemy.event import listen
    >>> engine = create_engine('sqlite:///example.db')
    >>> listen(engine, 'connect', set_sqlite_pragma)
    """
    ac = dbapi_connection.autocommit
    dbapi_connection.autocommit = True

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

    dbapi_connection.autocommit = ac

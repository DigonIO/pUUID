from typing import Generator, Literal
from sqlite3 import Connection

import pytest
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.event import listen
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool.base import (
    _ConnectionRecord,  # pyright: ignore[reportPrivateUsage]
)

from puuid import PUUID
from puuid.sqlalchemy import SqlPUUID

################################################################################
#### Types & Fixtures
################################################################################


class BaseORM(DeclarativeBase): ...


class UserUUID(PUUID[Literal["user"]]):
    _prefix = "user"


class UserORM(BaseORM):
    __tablename__ = "item_table"

    id: Mapped[UserUUID] = mapped_column(
        SqlPUUID(UserUUID, prefix_length=4), primary_key=True, default=UserUUID.factory
    )


class AddressUUID(PUUID[Literal["address"]]):
    _prefix = "address"


class AddressORM(BaseORM):
    __tablename__ = "address_table"

    id: Mapped[AddressUUID] = mapped_column(
        SqlPUUID(AddressUUID, prefix_length=7), primary_key=True
    )
    user_id: Mapped[AddressUUID] = mapped_column(
        SqlPUUID(UserUUID), ForeignKey(UserORM.id), default=None, nullable=True
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


@pytest.fixture()
def db(engine: Engine) -> Generator[Session, None, None]:
    db_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with db_factory() as db:
        try:
            yield db
        finally:
            db.rollback()
            db.close()


################################################################################
#### Tests
################################################################################


def test_serialize(db: Session) -> None:

    user = UserORM(id=UserUUID())
    address = AddressORM(id=AddressUUID())

    db.add(user)
    db.add(address)
    db.flush()


def test_deserialize(db: Session) -> None:

    user_id = UserUUID()
    user_ref_1 = UserORM(id=user_id)

    db.add(user_ref_1)
    db.flush()
    db.commit()

    user_ref_2: UserORM | None = db.query(UserORM).get(user_id)
    assert user_ref_2 is not None
    assert user_ref_1.id == user_ref_2.id

    address_ref_1 = AddressORM(id=AddressUUID())
    address_id = address_ref_1.id

    db.add(address_ref_1)
    db.flush()
    db.commit()

    address_ref_2: AddressORM | None = db.query(AddressORM).get(address_id)

    assert isinstance(address_ref_2, AddressORM)
    assert address_ref_2.user_id is None


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

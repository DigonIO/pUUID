---
description: "pUUID - Prefixed UUIDs for Python with Pydantic & SQLAlchemy support."
---

# Quick Start

Install **pUUID** from the [PyPI repositories](https://pypi.org/project/pUUID/) via pip:

```bash
pip install pUUID
```

For **SQLAlchemy** support, include the extra:

```bash
pip install 'pUUID[sqlalchemy]'
```

## Basic Usage

Define a custom PUUID class by inheriting from a versioned base and specifying a prefix.

```python
from typing import Literal
from uuid import UUID
from puuid import PUUIDv4

UserUUID = PUUIDv4[Literal["user"]]

# Generate a new random PUUID
user_id = UserUUID()
print(user_id)
# user_b100f10f-6876-4b61-984f-2c74be42fcd4

# Initialize from an existing UUID
uuid_obj = UUID('b100f10f-6876-4b61-984f-2c74be42fcd4')
user_id = UserUUID(uuid=uuid_obj)

# Serialization
serial: str = user_id.to_string()

# Deserialization
user_id: UserUUID = UserUUID.from_string(serial)
```

## Supported Variants

pUUID supports UUID versions 1, 3, 4, 5, 6, 7, and 8.

```{.python continuation}
from uuid import NAMESPACE_DNS
from puuid import PUUIDv5, PUUIDv7, PUUIDv8


# Time-based (ordered) UUIDs
EventUUID = PUUIDv7[Literal["evt"]]

print(EventUUID())
# evt_019b956e-ed25-70db-9d0a-0f30fb9047c2


# Name-based UUIDs
DomainUUID = PUUIDv5[Literal["dom"]]

dom_id = DomainUUID(namespace=NAMESPACE_DNS, name="digon.io")
print(dom_id)
# dom_cfbff0d1-9375-5685-968c-48ce8b15ae17


# Custom UUIDs
ChecksumUUID = PUUIDv8[Literal["chk"]]

chk_id = ChecksumUUID(a=0x123, b=0x456, c=0x789)
print(chk_id)
# chk_00000000-0123-8456-8000-000000000789
```

## Pydantic Integration

PUUIDs work as field types in Pydantic models with built-in validation.

```{.python continuation}
from pydantic import BaseModel

class User(BaseModel):
    user_id: UserUUID

user = User(user_id=UserUUID())
# Validation works with strings too
user = User(user_id="user_b100f10f-6876-4b61-984f-2c74be42fcd4")
```

## SQLAlchemy Integration

Use `SqlPUUID` to map PUUID classes to database columns.

```{.python continuation}
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from puuid.sqlalchemy import SqlPUUID

class BaseORM(DeclarativeBase): ...

class UserORM(BaseORM):
    __tablename__ = "users"

    id: Mapped[UserUUID] = mapped_column(
        SqlPUUID(UserUUID, prefix_length=4),
        primary_key=True,
        default=UserUUID.factory,
    )
```

!!! warning "Prefix Length Matching"
    The `prefix_length` argument in `SqlPUUID` is used to define the length of the underlying `VARCHAR` column.

    If your `_prefix` is `"user"` (4 characters), you must set `prefix_length=4`. If you later change the prefix to something longer without updating the column width via a migration, the database will raise an error or truncate the ID.

    **Calculation logic:**
    `prefix_length` + `1` (separator) + `36` (UUID) = Total Column Width.

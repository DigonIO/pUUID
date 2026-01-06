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

class UserUUID(PUUIDv4[Literal["user"]]):
    _prefix = "user"

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
